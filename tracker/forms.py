from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from .models import Habit, ProgressLog

class UserRegistrationForm(UserCreationForm):
    """
    Extended user registration form with enhanced validation and styling.

    This form provides a customized user registration experience with:
    - Email uniqueness validation
    - Username and password length requirements
    - Bootstrap-compatible form styling

    Fields:
        email (EmailField): User's email address with validation
        username (CharField): User's desired username with length validation
        password1 (CharField): User's password
        password2 (CharField): Password confirmation field

    Validates:
        - Email uniqueness
        - Minimum username length (4 characters)
        - Django's default password strength checks
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        validators=[
            MinLengthValidator(4, "Username must be at least 4 characters long")
        ]
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        help_text='Password must be at least 8 characters long and not entirely numeric.'
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """
        Validate that the email address is unique in the system.

        Raises:
            ValidationError: If the email is already registered

        Returns:
            str: Validated email address
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class CustomLoginForm(AuthenticationForm):
    """
    Customized login form with improved styling.

    Provides a tailored authentication experience with:
    - Bootstrap-compatible form styling
    - Standard Django authentication mechanism

    Fields:
        username (CharField): User's username for login
        password (CharField): User's password for authentication
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class HabitForm(forms.ModelForm):
    """
    ModelForm for creating and editing Habit instances.

    Provides a user-friendly interface for habit creation with:
    - Styled form fields
    - Validation based on Habit model constraints
    - Bootstrap-compatible form widgets

    Managed Fields:
        name (str): Name of the habit
        description (str, optional): Detailed description of the habit
        frequency (str): Frequency of habit performance
        difficulty (str): Subjective difficulty level of the habit

    Widgets:
        - Text input for name with placeholder
        - Textarea for description
        - Select dropdowns for frequency and difficulty
    """
    class Meta:
        model = Habit
        fields = [
            'name', 
            'description', 
            'frequency', 
            'difficulty'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter habit name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Optional description',
                'rows': 3
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select'
            })
        }




class ProgressLogForm(forms.ModelForm):
    """
    ModelForm for logging progress of a specific habit.

    Enables users to record detailed information about habit performance:
    - Status of habit completion
    - Optional notes
    - Optional time spent on the habit

    Managed Fields:
        status (str): Completion status (completed/skipped/missed)
        notes (str, optional): Additional context about habit performance
        duration_minutes (int, optional): Time invested in the habit

    Widgets:
        - Select dropdown for status
        - Textarea for notes
        - Number input for duration
    """
    class Meta:
        model = ProgressLog
        fields = ['status', 'notes', 'duration_minutes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional notes about your progress',
                'rows': 3
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Time spent (optional)'
            })
        }
