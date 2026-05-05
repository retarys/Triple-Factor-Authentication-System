import base64
from datetime import timedelta
from django.utils import timezone
import time
from io import BytesIO
import os
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
import cv2
from django.views import View
import face_recognition
import numpy as np
import pyotp
import qrcode
from django.contrib.auth.models import User
from .models import EventType, RegistrationSession, TOTPSecret, FaceTemplate, LoginSession, SecurityEvent
from .forms import RegistrationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

#Helpers for Login and Registration Sessions

def log_event(user=None, event_type=str):
    SecurityEvent.objects.create(user=user, event_type=event_type)
    return 


def check_loginsession(request,login_session):
    if not login_session:
        messages.error(request, "Login session missing")
        return False
    if login_session.created_at < timezone.now() - timedelta(minutes=5):
        messages.error(request, "Login session expired")
        return False
    return True

def get_login_session(request):
    session_id = request.session.get("login_session_id")
    if not session_id:
        messages.error(request,"Login session missing")
        return None
    try:
        return LoginSession.objects.get(session_id=session_id)
    except LoginSession.DoesNotExist:
        messages.error(request,"Login session not found")
        return None
    
def check_registersession(request,register_session):
    if not register_session:
        messages.error(request, "Registration session missing")
        return False
    if register_session.created_at < timezone.now() - timedelta(minutes=5):
        messages.error(request, "Registration session expired")
        return False
    return True

def get_registration_session(request):
    session_id = request.session.get("registration_session_id")
    if not session_id:
        messages.error(request,"Registration session missing")
        return None
    try:
        return RegistrationSession.objects.get(session_id=session_id)
    except RegistrationSession.DoesNotExist:
        messages.error(request,"Registration session not found")
        return None


def login_main(request):
    return render(request, 'login_main.html')



# Registration Views
def register(request):
    if request.method == 'POST':
        try:
            form = RegistrationForm(request.POST)

            if not form.is_valid():
                messages.error(request, "Please fix the errors in the form.")
                return redirect("register")  

            user_obj = User.objects.create_user(
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password1'])
            print("User created:", user_obj)
            log_event(user_obj, EventType.USER_CREATED_OK)
            register_session = RegistrationSession.objects.create(user=user_obj, pwd_ok=True)
            request.session["registration_session_id"] = str(register_session.session_id)
            return redirect('totp_setup')


        except IntegrityError:
            messages.error(request, "This username/email is already taken.")
            log_event(None, EventType.USER_CREATED_FAIL)
            return redirect("register")

        except Exception:
            messages.error(request, "Something went wrong during registration.")
            log_event(None, EventType.USER_CREATED_FAIL)
            return redirect("register")
        
    context = {
        'form': RegistrationForm()
    }
    return render(request, 'register.html', context)

def totp_setup(request):
    
    register_session = get_registration_session(request)
    if not check_registersession(request, register_session):
        messages.error(request, "Registration session has expired.")
        return redirect("register")
    if not register_session.pwd_ok:
        messages.error(request, "Password verification required.")
        return redirect("register")
    
    user = register_session.user
    if request.method == "POST":
        code = request.POST.get("totp_code")
        
        totp_secret_obj = TOTPSecret.objects.get(user=user)
        totp = pyotp.TOTP(totp_secret_obj.secret)

        if totp.verify(code, valid_window=1): 
            register_session.otp_ok = True
            register_session.save()
            messages.success(request, "TOTP setup is complete!")
            print("TOTP setup complete for user:", user.username)
            log_event(user, EventType.SETUP_OTP_OK)
            return redirect('facerec_setup')
        else:
            messages.error(request, "Invalid TOTP code.")
            log_event(user, EventType.SETUP_OTP_FAIL)

    totp_sercret_obj, created = TOTPSecret.objects.get_or_create(user=user, defaults={"secret" : pyotp.random_base32()})
    if not created:
        messages.error(request, "TOTP for this user already exists.")
        print("TOTP already exists for user:", user.username)
        return redirect("totp_setup")
    
    secret = totp_sercret_obj.secret
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="MyApp")
    
    img = qrcode.make(totp_uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'totp_setup.html', {'qr_code': image_base64})


class FaceRecSetup(View):
    def get(self, request):
        register_session = get_registration_session(request)
        if not check_registersession(request, register_session):
            messages.error(request, "Registration session has expired.")
            return redirect("register")
        if not register_session.otp_ok:
            messages.error(request, "TOTP verification required.")
            return redirect("totp_setup")
        return render(request, "facerec_setup.html")

    def capturePhoto(request):
        register_session = get_registration_session(request)
        if not check_registersession(request, register_session):
            messages.error(request, "Registration session has expired.")
            return redirect("register")
        if not register_session.otp_ok:
            messages.error(request, "TOTP verification required.")
            return redirect("totp_setup")
        
        user = register_session.user

        video = cv2.VideoCapture(0) 
        while True:
            check, frame = video.read()
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            cv2.imshow("Capturing",frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        showPic = cv2.imwrite(f"testimages/{user.username}.jpg",frame)
        # 8. shutdown the camera
        video.release()
        cv2.destroyAllWindows()

        messages.success(request, "Photo captured successfully!")


        img = face_recognition.load_image_file(f"testimages/{user.username}.jpg")
        img_encoding = face_recognition.face_encodings(img)[0]

        template, created = FaceTemplate.objects.get_or_create(user=user, 
                                                               template=img_encoding, 
                                                               image=f"face_templates/{user.username}.jpg")
        if not created:
            messages.error(request, "Face template for this user already exists.")
            return redirect("home")
        os.remove(f"testimages/{user.username}.jpg")

        register_session.face_ok = True
        register_session.save()
        print("Face recognition setup complete for user:", user.username)
        log_event(user, EventType.SETUP_FACE_OK)
        return redirect("home")


def home(request):
    return render(request, 'index.html')

@login_required(login_url="login_password")
def security_events(request):
    events = SecurityEvent.objects.all().order_by('-created_at')
    return render(request, 'security_events.html', {'events': events})

def login_password(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = User.objects.filter(username=username).first()
            if user and user.check_password(password):
                login_session = LoginSession.objects.create(user=user, pwd_ok=True)
                request.session["login_session_id"] = str(login_session.session_id)

                messages.success(request, "Password is correct")
                log_event(user, EventType.LOGIN_PWD_OK)
                return redirect('login_totp')
            else:
                messages.error(request, "Invalid username or password.")
                log_event(user, EventType.LOGIN_PWD_FAIL)
                return redirect('login_password')
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        log_event(None, EventType.LOGIN_PWD_FAIL)
    return render(request, 'login/login_password.html')

def login_totp(request):
    try:
        login_session = get_login_session(request)
        if not check_loginsession(request, login_session):
            return redirect("login_password")

        if not login_session.pwd_ok:
            messages.error(request,"Password verification required")
            return redirect("login_password")
        
        user = login_session.user
        if request.method == "POST":

            code = request.POST.get("totp_code")
            totp_secret_obj = TOTPSecret.objects.get(user=user)
            totp = pyotp.TOTP(totp_secret_obj.secret)

            if totp.verify(code, valid_window=1):
                login_session.otp_ok = True
                login_session.save()
                messages.success(request, "TOTP code is correct!")
                log_event(user, EventType.OTP_OK)
                return redirect('login_facerec')
            else:
                messages.error(request, "Invalid TOTP code.")
                log_event(user, EventType.OTP_FAIL)
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        log_event(None, EventType.OTP_FAIL)
    return render(request, 'login/login_totp.html')

def login_facerec(request):
    login_session = get_login_session(request)
    if not check_loginsession(request, login_session):
        return redirect("login_password")
    if not login_session.otp_ok:
        messages.error(request,"TOTP verification required")
        return redirect("login_totp")
    user = login_session.user

    target = FaceTemplate.objects.get(user=user).template
    target_name = user.username
    video_capture = cv2.VideoCapture(0)
    known_face_encodings = [target,]
    known_face_names = [target_name,]

    recognized_start_time = None
    unknown_start_time = None
    REQUIRED_SECONDS = 3
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and face enqcodings in the frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            if matches:
                if name in known_face_names:
                    if recognized_start_time is None:
                        recognized_start_time = time.time()
                
                    elapsed = time.time() - recognized_start_time
                    if elapsed >= REQUIRED_SECONDS:
                        login_session.face_ok = True
                        login_session.save()

                        if login_session.pwd_ok and login_session.otp_ok and login_session.face_ok:
                            login(request,user)

                            if "login_session_id" in request.session:
                                del request.session["login_session_id"]
                            messages.success(request, "Login successful!")
                            log_event(user, EventType.FACE_OK)
                            video_capture.release()
                            cv2.destroyAllWindows()      
                            return redirect("home")
                else:
                    if unknown_start_time is None:
                        unknown_start_time = time.time()
                    elapsed = time.time() - unknown_start_time
                    if elapsed >= REQUIRED_SECONDS:
                        messages.error(request, "Face not recognized. Please try again.")
                        log_event(user, EventType.FACE_FAIL)
                        video_capture.release()
                        cv2.destroyAllWindows()      
                        return redirect("login_totp")


        if len(face_locations) == 0:
            recognized_start_time = None
            unknown_start_time = None
            print("No face detected")
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()