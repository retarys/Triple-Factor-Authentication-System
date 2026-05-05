from django.contrib import admin
from .models import TOTPSecret, FaceTemplate, SecurityEvent, LoginSession, RegistrationSession

admin.site.register(TOTPSecret)
admin.site.register(FaceTemplate)
admin.site.register(SecurityEvent)
admin.site.register(RegistrationSession)
admin.site.register(LoginSession)
