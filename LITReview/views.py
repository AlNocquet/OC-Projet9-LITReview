from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignUpForm, ProfileUpdateForm, LoginForm 
# Create your views here.



def home_view(request):
    """
    Displays the home page for non-authenticated users.
    Redirects authenticated users to the feed ('flux').
    If the user is already authenticated, they are redirected to the main feed.
    """
    
    if request.user.is_authenticated:
        return redirect('flux')
    
    form = LoginForm()  # Formulaire
    return render(request, 'home.html', {'form': form})


def signup_view(request):
    """
    Django view handling user registration.

    - GET: displays an empty registration form.
    - POST: processes the submitted form data.
        - If valid: creates the user, logs them in, then redirects to the 'flux' page.
        - Otherwise: re-renders the form with error messages.
    """

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save() # crée l'utilisateur (Django impose (settings.py): mdp min 8 caractères; refuse mdp trop simples, mess. erreurs intégrés)
            login(request, user) # connecte l'utilisateur immédiatement
            return redirect('flux') # redirige vers la page principale
    else:
        form = SignUpForm()
    
    return render(request, 'auth/sign_up.html', {'form': form})


        
def login_view(request):
    """
    View handling user login.

    GET: displays login form
    POST: authenticates and logs user in
    """

    if request.user.is_authenticated:
        return redirect('flux')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('flux')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    else:
        form = LoginForm()

    return render(request, 'home.html', {'form': form})



def logout_view(request):
    """
    View handling user logout.
    Logs out and redirects to home page.
    """

    logout(request)
    return redirect('home')



@login_required
def profile_view(request):
    """
    View handling profile display and update.

    - GET: Display current user's information (username, email).
    - POST: Update user's profile information (username, email).
    """

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'auth/profile.html', {'form': form})



@login_required
def delete_account(request):
    """
    View allowing users to delete their own account.

    - GET: Displays a confirmation page asking the user if they really want to permanently delete their account.
    - POST: Deletes the user's account permanently, logs out the user immediately after deletion, and redirects to the home page with a confirmation message.

    Security measures:
    - Requires user to be authenticated (login required).
    - Account deletion only possible via POST request (to prevent accidental deletions).

    Template:
    - auth/delete_account.html

    Redirects:
    - Redirects to 'home' after successful deletion.
    """
        
    if request.method == "POST":
        user = request.user
        logout(request) # Déconnecte immédiatement après suppression
        user.delete()   # Supprime le compte utilisateur
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect('home')

    return render(request, 'auth/delete_account.html')



@login_required
def flux_view(request):
    """
    Placeholder view for the feed page (flux).
    Accessible uniquement si l'utilisateur est connecté.
    """

    return render(request, 'feed/flux.html')