from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Habit, ProgressLog
from .forms import UserRegistrationForm, CustomLoginForm, HabitForm, ProgressLogForm
from django.utils import timezone


def home(request):
    """
    Render the home page of the application.

    This view serves as the landing page for the HabitFlow application. 
    It is accessible to all users, including unauthenticated visitors.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'home.html' template.
    """
    return render(request, 'home.html')


def register_view(request):
    """
    Handle user registration for new accounts.

    This view manages the user registration process. If the user is already 
    authenticated, they are redirected to the dashboard. For POST requests, 
    it validates the registration form and creates a new user account.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: 
            - Renders 'authentication/register.html' with registration form
            - Redirects to 'dashboard' upon successful registration
    
    Behaviors:
        - Redirects authenticated users to dashboard
        - Creates user account on valid form submission
        - Displays form errors on invalid input
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
    Handle user login authentication.

    This view manages the login process for existing users. If the user is 
    already authenticated, they are redirected to the dashboard. For POST 
    requests, it validates credentials and logs in the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse:
            - Renders 'authentication/login.html' with login form
            - Redirects to 'dashboard' upon successful authentication
    
    Behaviors:
        - Redirects authenticated users to dashboard
        - Authenticates users with valid credentials
        - Displays error messages for invalid login attempts
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
    Handle user logout and session termination.

    This view logs out the current user and redirects them to the home page. 
    It also displays a farewell message with the user's username.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to 'home' page after logging out the user.
    
    Behaviors:
        - Terminates the current user's session
        - Displays a logout confirmation message
    """
    username = request.user.username
    logout(request)
    messages.info(request, f'You have been logged out, {username}. See you soon!')
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Render the user's personal dashboard.

    This view is only accessible to authenticated users. It retrieves 
    and displays the user's habits and recent progress logs.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders 'authentication/dashboard.html' with user's habits
                      and recent progress logs.
    
    Requires:
        - User authentication
    
    Context Variables:
        - habits: QuerySet of Habit objects owned by the current user
        - recent_logs: Last 5 ProgressLog entries for the user's habits
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
    Provide a view for creating new habits.

    This view allows authenticated users to create a new habit. For POST 
    requests, it validates the habit form and saves a new Habit instance.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse:
            - Renders 'habit_form.html' with habit creation form
            - Redirects to 'dashboard' upon successful habit creation
    
    Requires:
        - User authentication

    Behaviors:
        - Associates new habit with the current user
        - Displays success message on habit creation
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
    Provide a view for editing an existing habit.

    This view allows authenticated users to modify details of a specific habit. 
    It ensures the habit belongs to the current user.

    Args:
        request (HttpRequest): The HTTP request object.
        habit_id (int): The primary key of the habit to be edited.

    Returns:
        HttpResponse:
            - Renders 'habit_form.html' with habit edit form
            - Redirects to 'dashboard' upon successful habit update

    Raises:
        Http404: If the habit does not exist or does not belong to the user
    
    Requires:
        - User authentication

    Behaviors:
        - Populates form with existing habit details
        - Displays success message on habit update
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
    Provide a view for deleting a specific habit.

    This view allows authenticated users to delete one of their habits. 
    It requires a POST request to confirm the deletion and ensures the 
    habit belongs to the current user.

    Args:
        request (HttpRequest): The HTTP request object.
        habit_id (int): The primary key of the habit to be deleted.

    Returns:
        HttpResponse:
            - Renders 'habit_confirm_delete.html' for confirmation
            - Redirects to 'dashboard' after successful deletion

    Raises:
        Http404: If the habit does not exist or does not belong to the user
    
    Requires:
        - User authentication

    Behaviors:
        - Displays confirmation page on GET request
        - Deletes habit and redirects on POST request
        - Displays success message after deletion
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
    Provide a view for logging progress on a specific habit.

    This view allows authenticated users to log their progress for a particular 
    habit. It supports creating new progress logs and updating existing logs 
    for the same habit and date.

    Args:
        request (HttpRequest): The HTTP request object.
        habit_id (int): The primary key of the habit to log progress for.

    Returns:
        HttpResponse:
            - Renders 'progress_log_form.html' with progress logging form
            - Redirects to 'dashboard' upon successful progress log

    Raises:
        Http404: If the habit does not exist or does not belong to the user
    
    Requires:
        - User authentication

    Behaviors:
        - Checks for existing progress log on the same date
        - Updates existing log or creates a new log
        - Displays success message after logging progress
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

