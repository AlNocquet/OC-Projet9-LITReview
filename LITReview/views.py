from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import SignUpForm, ProfileUpdateForm, LoginForm, FollowUserForm, BlockUserForm
from .models import UserFollows

from .models import UserFollows, BlockedUser
from .forms import FollowUserForm, BlockUserForm


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
def subscriptions_view(request):
    """
    Handles user subscriptions and blocking logic from a unified interface.

    GET:
    - Renders the subscriptions page with:
      - A form to follow users
      - A form to block users
      - Lists of followed users, followers, and blocked users

    POST:
    - Processes submitted forms:
      - Follows a user if allowed (not already followed or blocked)
      - Blocks a user and removes any existing follow relationships

    Context variables:
    - form: FollowUserForm (for following a user)
    - block_form: BlockUserForm (for blocking a user)
    - followed_users: QuerySet of users the current user is following
    - followers: QuerySet of users who follow the current user
    - blocked_users: QuerySet of users the current user has blocked

    Template:
    - auth/subscriptions.html
    """

    user = request.user
    form = FollowUserForm()
    block_form = BlockUserForm()

    if request.method == 'POST':
        if 'block' in request.POST:
            block_form = BlockUserForm(request.POST)
            if block_form.is_valid():
                username_to_block = block_form.cleaned_data['username'].strip()
                try:
                    to_block = User.objects.get(username__iexact=username_to_block)
                    if to_block == user:
                        messages.error(request, "Tu ne peux pas te bloquer toi-même.")
                    elif BlockedUser.objects.filter(user=user, blocked_user=to_block).exists():
                        messages.warning(request, f"{to_block.username} est déjà bloqué.")
                    else:
                        BlockedUser.block(user, to_block)
                        messages.success(request, f"{to_block.username} a été bloqué.")
                        return redirect('subscriptions')
                except User.DoesNotExist:
                    messages.error(request, "Cet utilisateur n'existe pas.")
        else:
            form = FollowUserForm(request.POST)
            if form.is_valid():
                username_to_follow = form.cleaned_data['username'].strip()
                try:
                    to_follow = User.objects.get(username__iexact=username_to_follow)
                    if to_follow == user:
                        messages.error(request, "Tu ne peux pas te suivre toi-même.")
                    elif BlockedUser.objects.filter(user=to_follow, blocked_user=user).exists():
                        messages.error(request, f"Tu ne peux pas suivre {to_follow.username}.")
                    elif BlockedUser.objects.filter(user=user, blocked_user=to_follow).exists():
                        messages.error(request, f"Tu ne peux pas suivre {to_follow.username} tant que tu l'as bloqué.")
                    elif UserFollows.objects.filter(user=user, followed_user=to_follow).exists():
                        messages.warning(request, f"Tu suis déjà {to_follow.username}.")
                    else:
                        UserFollows.objects.create(user=user, followed_user=to_follow)
                        messages.success(request, f"Tu suis maintenant {to_follow.username}.")
                        return redirect('subscriptions')
                except User.DoesNotExist:
                    messages.error(request, "Cet utilisateur n'existe pas.")

    followed_users = UserFollows.objects.filter(user=user)
    followers = UserFollows.objects.filter(followed_user=user)
    blocked_users = BlockedUser.objects.filter(user=user)

    return render(request, 'auth/subscriptions.html', {
        'form': form,
        'block_form': block_form,
        'followed_users': followed_users,
        'followers': followers,
        'blocked_users': blocked_users
    })



@login_required
def unfollow_view(request, user_id):
    """
    Handles the action of unfollowing a user.

    - Only accessible via GET request.
    - Removes the UserFollows relationship from the current user to the target user (if it exists).

    Parameters:
    - user_id: ID of the user to unfollow

    Redirects:
    - To 'subscriptions' with a success or error message

    Template:
    - auth/subscriptions.html
    """

    try:
        to_unfollow = User.objects.get(pk=user_id)
        UserFollows.objects.filter(user=request.user, followed_user=to_unfollow).delete()
        messages.success(request, f"Vous ne suivez plus {to_unfollow.username}.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('subscriptions')



@login_required
def unblock_user_view(request, user_id):
    """
    Handles the action of unblocking a user.

    - Deletes the BlockedUser relationship if it exists.

    Parameters:
    - user_id: ID of the user to unblock

    Redirects:
    - To 'subscriptions' with a success or error message

    Template:
    - auth/subscriptions.html
    """

    try:
        to_unblock = User.objects.get(pk=user_id)
        blocked_relation = BlockedUser.objects.filter(user=request.user, blocked_user=to_unblock)
        if blocked_relation.exists():
            blocked_relation.delete()
            messages.success(request, f"{to_unblock.username} a été débloqué.")
        else:
            messages.info(request, f"{to_unblock.username} n'était pas bloqué.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('subscriptions')




@login_required
def block_from_follower_view(request, user_id):
    """
    Handles the action of blocking a user directly from the followers list.

    - Removes any follow relationship between the two users.
    - Creates a BlockedUser entry if not already blocked.

    Parameters:
    - user_id: ID of the user to block

    Redirects:
    - To 'subscriptions' with a success or error message

    Template:
    - auth/subscriptions.html
    """

    try:
        to_block = User.objects.get(pk=user_id)
        BlockedUser.block(request.user, to_block)
        messages.success(request, f"{to_block.username} a été bloqué.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('subscriptions')




@login_required
def flux_view(request):
    """
    Placeholder view for the feed page (flux).
    Accessible uniquement si l'utilisateur est connecté.
    """

    return render(request, 'feed/flux.html')