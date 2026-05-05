from datetime import timedelta
from django.utils import timezone
import time
import cv2 
import face_recognition
from matplotlib.pylab import size
from simple_facerec import SimpleFacerec
import numpy as np

# sfr = SimpleFacerec()
# sfr.load_encoding_images("images/")

# cap = cv2.VideoCapture(0)

# target = "Alisher"
# while True:
#     ret, frame = cap.read()

#     face_locations, face_names = sfr.detect_known_faces(frame)
#     for face_loc, name in zip(face_locations, face_names):
#         top, left, bottom, right = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
#         cv2.putText(frame, name, (right, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
#     print(face_names)
#     cv2.imshow('frame', frame)

#     key = cv2.waitKey(1)
#     if key == ord('q'):
#         break
#     if target in face_names:
#         print("target found")
#         break


# cap.release()
# cv2.destroyAllWindows()








# img2 = cv2.imread('images/Murad.jpg')
# rgb_img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2RGB)
# img2_encoding = face_recognition.face_encodings(rgb_img2)[0]

# result = face_recognition.compare_faces([img_encoding],img2_encoding)
# print(result)
# print(type(img_encoding))

# cv2.imshow('image',img)
# cv2.imshow('image2',img2)
# cv2.waitKey(0)



def capturePhoto():
    name = input("Enter your name: ")
    print("Taking photo in 3 seconds...")
    video = cv2.VideoCapture(0) 
    while True:
        check, frame = video.read()
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        cv2.imshow("Capturing",frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    showPic = cv2.imwrite(f"testimages/{name}.jpg",frame)
    # 8. shutdown the camera
    video.release()
    cv2.destroyAllWindows()
    return showPic, name

def addFace(target):
    sfr = SimpleFacerec()
    sfr.load_encoding_images("testimages/")


def test(target):
    sfr = SimpleFacerec()
    sfr.load_encoding_images("testimages/")

    cap = cv2.VideoCapture(0)
    ml = 0
    while True:
        ret, frame = cap.read()


        face_locations, face_names = sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            top, left, bottom, right = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (right, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
        print(face_names)
        cv2.imshow('frame', frame)

        key = cv2.waitKey(2)
        if key == ord('q'):
            break
        if target in face_names:
            ml += 1
            if ml == 5:
                print("target found")
                break

    cap.release()
    cv2.destroyAllWindows()





def login_facerec():


    img = cv2.imread('images/Alisher.jpg')
    rgb_img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img_encoding = face_recognition.face_encodings(rgb_img)[0]
    video_capture = cv2.VideoCapture(0)
    known_face_encodings = [img_encoding,]
    known_face_names = ['Alisher',]

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
                        print("target found")
                        video_capture.release()
                        cv2.destroyAllWindows()      
                else:
                    if unknown_start_time is None:
                        unknown_start_time = time.time()
                    elapsed = time.time() - unknown_start_time
                    if elapsed >= REQUIRED_SECONDS:
                        print("Face not recognized. Please try again.")
                        video_capture.release()
                        cv2.destroyAllWindows()      
            print(recognized_start_time, unknown_start_time)
            print(type(matches))

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

def main():
    login_facerec()

if __name__ == "__main__":
    main()
