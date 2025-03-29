from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """
    Custom form for user registration.

    Inherits from Django's UserCreationForm and restricts visible fields to:
    - Username
    - Email
    - Password
    - Password confirmation

    Includes placeholders and styling for improved user experience.
    """

    email = forms.EmailField(
        required=True,
        label="Adresse email",
        help_text="Obligatoire. Utilisé pour réinitialiser votre mot de passe.",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Adresse email',
            'style': 'text-align: center; color: #666;',
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Nom d'utilisateur",
            'style': 'text-align: center; color: #666;',
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': "Mot de passe",
            'style': 'text-align: center; color: #666;',
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': "Confirmer mot de passe",
            'style': 'text-align: center; color: #666;',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    """
    Custom form for updating user profile information.

    Allows the user to update:
    - Username
    - Email

    Connected to Django's built-in User model.
    """

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nom d\'utilisateur',
            'email': 'Adresse email'
        }


class LoginForm(AuthenticationForm):
    """
    Custom form for user authentication.

    Allows the user to log in using:
    - Username
    - Password

    Includes styled input fields for a consistent user interface.
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Nom d'utilisateur",
            'style': 'text-align: center; color: #666;',
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': "Mot de passe",
            'style': 'text-align: center; color: #666;',
        })
    )
