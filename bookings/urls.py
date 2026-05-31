from django.urls import path
from . import views

urlpatterns = [
    path('doctors/', views.DoctorListView.as_view()),
    path('doctors/<int:doctor_id>/slots/', views.TimeSlotListView.as_view()),
    path('appointments/', views.AppointmentCreateView.as_view()),
    path('appointments/my/', views.AppointmentListView.as_view()),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view()),
]
