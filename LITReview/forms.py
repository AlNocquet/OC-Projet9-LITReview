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
    For ModelForms.
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


class SignUpForm(BaseForm,UserCreationForm):
    """
    Custom form for user registration.

    Inherits from BaseForm and Django's UserCreationForm, and restricts visible fields to:
    - Username
    - Email
    - Password
    - Password confirmation
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class ProfileUpdateForm(BaseModelForm):
    """
    Custom form for updating user profile information.

    Fields:
    - Username
    - Email

    Inherits from BaseModelForm.
    """

    class Meta:
        model = User
        fields = ['username', 'email']



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
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'image': 'Image',
        }


class ReviewForm(forms.ModelForm):
    """
    Form to create or update a Review.
    Includes: headline (title), body (comment), rating (0 - 5).
    """
    class Meta:
            model = Review
            fields = ['headline', 'body', 'rating']
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
    title = forms.CharField(label="Titre du livre ou article", max_length=128)
    description = forms.CharField(label="Description", widget=forms.Textarea, required=False)
    image = forms.ImageField(label="Image", required=False)

    # Champs de la critique
    headline = forms.CharField(label="Titre de la critique", max_length=128)
    body = forms.CharField(label="Texte", widget=forms.Textarea, required=False)
    rating = forms.IntegerField(label="Note", min_value=0, max_value=5)