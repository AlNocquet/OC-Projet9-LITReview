from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Ticket, Review


class BaseForm(forms.Form):
    """
    Custom base form:
    - Ensures consistent CSS styling across all form fields
    - Automatically assigns placeholder text if not explicitly set
    - Suppresses default labels to delegate visual control to templates <h>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                continue
            placeholder = field.label or name.replace('_', ' ').capitalize()
            field.widget.attrs.update({
                'placeholder': placeholder,
                'style': 'text-align: center; color: #666;',
                'class': 'form-control'
            })
            field.label = ''


class BaseModelForm(forms.ModelForm):
    """
    Custom base ModelForm for consistent field styling and placeholders.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                continue
            placeholder = field.label or name.replace('_', ' ').capitalize()
            field.widget.attrs.update({
                'placeholder': placeholder,
                'style': 'text-align: center; color: #666;',
                'class': 'form-control'
            })
            field.label = ''


class SignUpForm(BaseForm, UserCreationForm):
    """
    Custom form for user registration.
    Fields: username, email (must be unique), password1, password2.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email


class ProfileUpdateForm(BaseModelForm):
    """
    Custom form for updating user profile.
    Fields: username, email (must be unique among other users).
    """

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email


class ProfileUpdateForm(BaseModelForm):
    """
    Custom form for updating user profile information.
    Fields: Username, Email.
    """

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Cherche un autre user avec cet email
        if User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre utilisateur.")
        return email


class LoginForm(BaseForm, AuthenticationForm):
    """
    Custom form for user authentication.

    Allows the user to log in using:
    - Username
    - Password

    Inherits from Django's AuthenticationForm and BaseForm.
    """

    pass


class FollowUserForm(BaseForm):
    """
    Form to enter the username of a user to follow.

    Field:
    - username: The username of the user to follow (CharField).

    Inherits from BaseForm.
    """

    username = forms.CharField(label="Nom d'utilisateur", max_length=150)


class BlockUserForm(forms.Form):
    """
    Form to enter the username of a user to block.

    Field:
    - username: The username of the user to block (CharField).

    Inherits from Django's base Form class.
    """

    username = forms.CharField(
        label="",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': "Nom d'utilisateur"
        })
    )


class TicketForm(forms.ModelForm):
    """
    Form to create or update a Ticket.
    Includes: title, description, image.
    """

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'maxlength': 128}),
            'description': forms.Textarea(attrs={'maxlength': 2048}),
        }


class ReviewForm(forms.ModelForm):
    """
    Form to create or update a Review.
    Includes: headline (title), body (comment), rating (0 - 5).
    """
    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']
        widgets = {
            'headline': forms.TextInput(attrs={'maxlength': 128}),
            'body': forms.Textarea(attrs={'maxlength': 8192}),
        }
        labels = {
            'headline': 'Titre',
            'body': 'Texte',
            'rating': 'Note',
        }

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['rating'].widget = forms.NumberInput(attrs={
                'min': 0,
                'max': 5,
                'step': 1
            })

    
class TicketReviewForm(forms.Form):
    """
    Form to create Ticket AND Review.
    Includes: title, description, image.
    Includes: headline (title), body (comment), rating (0 - 5).
    """

     # Champs du ticket
    title = forms.CharField(
        label="Titre du livre ou article", max_length=128, required=True,
        widget=forms.TextInput(attrs={'maxlength': 128})
    )
    description = forms.CharField(
        label="Description", required=True,
        widget=forms.Textarea(attrs={'maxlength': 2048})
    )
    image = forms.ImageField(
        label="Image", required=False
    )

    # Champs de la critique
    headline = forms.CharField(
        label="Titre de la critique", max_length=128, required=True,
        widget=forms.TextInput(attrs={'maxlength': 128})
    )
    body = forms.CharField(
        label="Commentaire", required=True,
        widget=forms.Textarea(attrs={'maxlength': 8192})
    )
    rating = forms.IntegerField(
        label="Note", min_value=0, max_value=5, required=True
    )