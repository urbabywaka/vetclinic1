# appointments/urls.py - FINAL WORKING VERSION
from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:pk>/edit/', views.edit_appointment, name='edit_appointment'),
    path('appointments/<int:pk>/delete/', views.delete_appointment, name='delete_appointment'),
    path('book/', views.book_appointment, name='book_appointment'),
    
    # Admin URLs - USE 'panel/' PREFIX (NOT 'admin/')
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Separate action URLs with 'panel/' prefix
    path('panel/approve/<int:pk>/', views.admin_approve_appointment, name='admin_approve_appointment'),
    path('panel/reject/<int:pk>/', views.admin_reject_appointment, name='admin_reject_appointment'),
    path('panel/complete/<int:pk>/', views.admin_complete_appointment, name='admin_complete_appointment'),
    path('panel/cancel/<int:pk>/', views.admin_cancel_appointment, name='admin_cancel_appointment'),
    
    # Other admin functions
    path('panel/edit/<int:pk>/', views.admin_edit_appointment, name='admin_edit_appointment'),
    path('panel/user/<int:user_id>/', views.admin_view_user, name='admin_view_user'),
]