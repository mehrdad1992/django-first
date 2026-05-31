from django.contrib import admin

# Register your models here.
from .models import Doctor, TimeSlot, Appointment

admin.site.register(Doctor)
admin.site.register(TimeSlot)
admin.site.register(Appointment)