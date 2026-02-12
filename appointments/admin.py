# appointments/admin.py
from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet_name', 'species', 'appointment_date', 'appointment_time', 'user')
    list_filter = ('appointment_date', 'species', 'user')
    search_fields = ('pet_name', 'species', 'reason', 'user__username')
    ordering = ('-appointment_date', '-appointment_time')
    date_hierarchy = 'appointment_date'