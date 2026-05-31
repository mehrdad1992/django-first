from celery import shared_task
from django.utils import timezone


@shared_task
def send_appointment_reminder(appointment_id):
    """
    Send reminder notification for an upcoming appointment.
    In production this would send email/SMS.
    """
    from bookings.models import Appointment  # avoid circular import

    try:
        appointment = Appointment.objects.select_related(
            'patient', 'time_slot__doctor'
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"

    # در production اینجا email یا SMS می‌فرستی
    # الان فقط log می‌کنیم
    patient_name = appointment.patient.get_full_name() or appointment.patient.username
    doctor_name = appointment.time_slot.doctor.full_name
    slot_time = appointment.time_slot.start_time

    message = (
        f"Reminder: {patient_name}, your appointment with "
        f"Dr. {doctor_name} is scheduled for {slot_time}"
    )

    print(f"[NOTIFICATION] {message}")
    return message


@shared_task
def send_appointment_confirmation(appointment_id):
    """Send confirmation right after booking."""
    from bookings.models import Appointment

    try:
        appointment = Appointment.objects.select_related(
            'patient', 'time_slot__doctor'
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"

    patient_name = appointment.patient.get_full_name() or appointment.patient.username
    doctor_name = appointment.time_slot.doctor.full_name

    message = (
        f"Confirmation: {patient_name}, your appointment with "
        f"Dr. {doctor_name} has been booked successfully."
    )

    print(f"[NOTIFICATION] {message}")
    return message
