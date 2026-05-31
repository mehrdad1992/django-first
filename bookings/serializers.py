from rest_framework import serializers
from django.db import transaction
from .models import Doctor, TimeSlot, Appointment


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'bio']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'doctor', 'start_time', 'end_time', 'is_available']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'timeslot', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        with transaction.atomic():
            slot = TimeSlot.objects.select_for_update().get(
                id=validated_data['timeslot'].id,
                is_available=True
            )
            slot.is_available = False
            slot.save()
            return Appointment.objects.create(user=user, timeslot=slot)
