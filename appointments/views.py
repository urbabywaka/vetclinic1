from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Appointment
from .forms import AppointmentForm, RegisterForm, AdminAppointmentForm


def home(request):
    return render(request, 'appointments/home.html')


def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Check if user is admin/superuser
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'appointments/login.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            
            # Check if admin created account
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'appointments/register.html', {'form': form})


def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully! Waiting for admin approval.")
            return redirect('dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/book_appointment.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Check if admin is trying to access user dashboard
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    
    # Get user's appointments
    appointments = Appointment.objects.filter(user=request.user)
    
    # Filter by status if specified
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    today = date.today()
    appointments_today = appointments.filter(appointment_date=today).count()
    
    # Status counts (for ALL appointments, not filtered)
    all_user_appointments = Appointment.objects.filter(user=request.user)
    pending_count = all_user_appointments.filter(status='pending').count()
    approved_count = all_user_appointments.filter(status='approved').count()
    rejected_count = all_user_appointments.filter(status='rejected').count()
    completed_count = all_user_appointments.filter(status='completed').count()
    
    context = {
        'appointments': appointments,
        'appointments_today': appointments_today,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'completed_count': completed_count,
        'is_admin': False,
    }
    return render(request, "appointments/dashboard.html", context)


@login_required
def admin_dashboard(request):
    # Check if user is admin
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    # Get all data
    all_appointments = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')
    all_users = User.objects.all()
    
    # Statistics
    today = date.today()
    total_appointments = all_appointments.count()
    total_users = all_users.count()
    appointments_today = all_appointments.filter(appointment_date=today).count()
    
    # Status counts
    pending_appointments = all_appointments.filter(status='pending').count()
    approved_appointments = all_appointments.filter(status='approved').count()
    rejected_appointments = all_appointments.filter(status='rejected').count()
    completed_appointments = all_appointments.filter(status='completed').count()
    
    # Recent appointments (last 10)
    recent_appointments = all_appointments[:10]
    
    # Today's appointments
    today_appointments = all_appointments.filter(appointment_date=today)
    
    # Users with most appointments
    top_users = User.objects.annotate(
        appointment_count=Count('appointment')
    ).order_by('-appointment_count')[:5]
    
    context = {
        'all_appointments': all_appointments,
        'recent_appointments': recent_appointments,
        'today_appointments': today_appointments,
        'all_users': all_users,
        'top_users': top_users,
        'total_appointments': total_appointments,
        'total_users': total_users,
        'appointments_today': appointments_today,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'rejected_appointments': rejected_appointments,
        'completed_appointments': completed_appointments,
        'today': today,
    }
    return render(request, "appointments/admin_dashboard.html", context)


@login_required
def admin_edit_appointment(request, pk):
    """Admin edit appointment with notes"""
    if not request.user.is_superuser:
        messages.error(request, "Admin privileges required.")
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AdminAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Appointment for {appointment.pet_name} updated successfully!")
            return redirect('admin_dashboard')
    else:
        form = AdminAppointmentForm(instance=appointment)
    
    return render(request, 'appointments/admin_edit_appointment.html', {
        'form': form,
        'appointment': appointment
    })


@login_required
def admin_view_user(request, user_id):
    """View user details and their appointments"""
    if not request.user.is_superuser:
        messages.error(request, "Admin privileges required.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    user_appointments = Appointment.objects.filter(user=user).order_by('-appointment_date')
    
    context = {
        'view_user': user,
        'user_appointments': user_appointments,
        'appointment_count': user_appointments.count(),
    }
    return render(request, 'appointments/admin_view_user.html', context)


@login_required
def admin_approve_appointment(request, pk):
    """Approve appointment"""
    if not request.user.is_superuser:
        messages.error(request, "Admin privileges required.")
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'approved'
    appointment.save()
    messages.success(request, f"✅ Appointment for {appointment.pet_name} has been approved!")
    return redirect('admin_dashboard')


@login_required
def admin_reject_appointment(request, pk):
    """Reject appointment"""
    if not request.user.is_superuser:
        messages.error(request, "Admin privileges required.")
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'rejected'
    appointment.save()
    messages.success(request, f"❌ Appointment for {appointment.pet_name} has been rejected!")
    return redirect('admin_dashboard')


@login_required
def admin_complete_appointment(request, pk):
    """Mark appointment as completed"""
    if not request.user.is_superuser:
        messages.error(request, "Admin privileges required.")
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'completed'
    appointment.save()
    messages.success(request, f"✅ Appointment for {appointment.pet_name} marked as completed!")
    return redirect('admin_dashboard')


@login_required
def admin_cancel_appointment(request, pk):
    """Cancel appointment"""
    if not request.user.is_superuser:
        messages.error(request, "Admin privileges required.")
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, f"⚠️ Appointment for {appointment.pet_name} has been cancelled!")
    return redirect('admin_dashboard')


@login_required
def add_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            if appointment.appointment_date < date.today():
                messages.error(request, "You cannot book an appointment in the past.")
                return redirect("add_appointment")
            appointment.save()
            messages.success(request, "Appointment booked successfully! Waiting for approval.")
            return redirect("dashboard")
    else:
        form = AppointmentForm()
    return render(request, "appointments/appointment_form.html", {'form': form})


@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    
    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect('dashboard')
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'appointments/appointment_form.html', 
                  {'form': form, 'appointment': appointment})


@login_required
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully!")
        return redirect('dashboard')
    
    return render(request, 'appointments/confirm_delete.html', {'appointment': appointment})