from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Habit Management URLs
    path('habit/create/', views.create_habit, name='create_habit'),
    path('habit/<int:habit_id>/edit/', views.edit_habit, name='edit_habit'),
    path('habit/<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
    path('habit/<int:habit_id>/log/', views.log_habit_progress, name='log_habit_progress'),
]