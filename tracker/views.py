from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Habit, ProgressLog
from .forms import UserRegistrationForm, CustomLoginForm, HabitForm, ProgressLogForm
from django.utils import timezone


def home(request):
    """
    Home view
    """
    return render(request, 'home.html')


def register_view(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            messages.success(request, f'Account created for {username}! Welcome to HabitFlow.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """
    User login view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """
    User logout view
    """
    username = request.user.username
    logout(request)
    messages.info(request, f'You have been logged out, {username}. See you soon!')
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    User dashboard view with recent progress logs
    """
    # Get the user's habits
    habits = Habit.objects.filter(user=request.user)
    
    # Get recent progress logs across all habits, ordered by most recent
    recent_logs = ProgressLog.objects.filter(habit__user=request.user).order_by('-date')[:5]
    
    context = {
        'habits': habits,
        'recent_logs': recent_logs
    }
    
    return render(request, 'authentication/dashboard.html', context)


@login_required
def create_habit(request):
    """
    View to create a new habit
    """
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, f'Habit "{habit.name}" created successfully!')
            return redirect('dashboard')
    else:
        form = HabitForm()
    
    return render(request, 'habit_form.html', {
        'form': form,
        'title': 'Create New Habit'
    })


@login_required
def edit_habit(request, habit_id):
    """
    View to edit an existing habit
    """
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Habit "{habit.name}" updated successfully!')
            return redirect('dashboard')
    else:
        form = HabitForm(instance=habit)
    
    return render(request, 'habit_form.html', {
        'form': form,
        'title': f'Edit Habit: {habit.name}'
    })


@login_required
def delete_habit(request, habit_id):
    """
    View to delete a habit
    """
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    
    if request.method == 'POST':
        habit_name = habit.name
        habit.delete()
        messages.success(request, f'Habit "{habit_name}" deleted successfully.')
        return redirect('dashboard')
    
    return render(request, 'habit_confirm_delete.html', {
        'habit': habit
    })


@login_required
def log_habit_progress(request, habit_id):
    """
    View to log progress for a specific habit
    """
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    
    if request.method == 'POST':
        form = ProgressLogForm(request.POST)
        if form.is_valid():
            # Check if a log for this habit and date already exists
            existing_log = ProgressLog.objects.filter(
                habit=habit, 
                date=form.cleaned_data.get('date', timezone.now().date())
            ).first()
            
            if existing_log:
                # Update existing log
                form = ProgressLogForm(request.POST, instance=existing_log)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Progress updated for "{habit.name}"')
            else:
                # Create new log
                progress_log = form.save(commit=False)
                progress_log.habit = habit
                progress_log.save()
                messages.success(request, f'Progress logged for "{habit.name}"')
            
            return redirect('dashboard')
    else:
        form = ProgressLogForm()
    
    return render(request, 'progress_log_form.html', {
        'form': form,
        'habit': habit
    })

