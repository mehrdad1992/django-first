from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from .models import Doctor, TimeSlot, Appointment
from .serializers import DoctorSerializer, TimeSlotSerializer, AppointmentSerializer


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]


# class TimeSlotListView(generics.ListAPIView):
#     serializer_class = TimeSlotSerializer
#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         return TimeSlot.objects.filter(
#             doctor_id=self.kwargs['doctor_id'],
#             is_available=True
#         )

class TimeSlotListView(generics.ListAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        cache_key = f"timeslots_doctor_{doctor_id}"
        
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        qs = TimeSlot.objects.filter(
            doctor_id=doctor_id,
            is_available=True
        )
        cache.set(cache_key, qs, timeout=60 * 5)  # 5 دقیقه
        return qs


class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except TimeSlot.DoesNotExist:
            raise ValidationError("این اسلات دیگر در دسترس نیست.")
        cache.delete(f"timeslots_doctor_{TimeSlot.doctor_id}")
        from notifications.tasks import send_appointment_confirmation, send_appointment_reminder

        # داخل create یا perform_create، بعد از ذخیره:
        appointment = serializer.save()

        # تأییدیه فوری (async)
        send_appointment_confirmation.delay(appointment.id)

        # reminder یک ساعت قبل از وقت
        from django.utils import timezone
        from datetime import timedelta

        reminder_time = appointment.time_slot.start_time - timedelta(hours=1)
        send_appointment_reminder.apply_async(
            args=[appointment.id],
            eta=reminder_time
        )


class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).select_related('timeslot')


class AppointmentCancelView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Appointment, id=self.kwargs['pk'], user=self.request.user)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.timeslot.is_available = True
            instance.timeslot.save()
            instance.delete()
