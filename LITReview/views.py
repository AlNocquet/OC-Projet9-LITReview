from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import BlockedUser 

from .forms import SignUpForm, ProfileUpdateForm, LoginForm, FollowUserForm, BlockUserForm
from .models import UserFollows

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
    View to manage subscriptions and user blocking from a single page.

    - GET: Displays forms for following and blocking users,
        along with lists of followed users, followers, and blocked users.
    - POST: Processes either follow or block form based on the submitted data.

    Context:
    - form: FollowUserForm for subscribing to users
    - block_form: BlockUserForm for blocking users
    - followed_users: users the current user is following
    - followers: users following the current user
    - blocked_users: users the current user has blocked

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
                username_to_block = block_form.cleaned_data['username']
                try:
                    to_block = User.objects.get(username=username_to_block)
                    if to_block == user:
                        messages.error(request, "Tu ne peux pas te bloquer toi-même.")
                    elif BlockedUser.objects.filter(user=user, blocked_user=to_block).exists():
                        messages.warning(request, f"{username_to_block} est déjà bloqué.")
                    else:
                        UserFollows.objects.filter(user=user, followed_user=to_block).delete()
                        UserFollows.objects.filter(user=to_block, followed_user=user).delete()
                        BlockedUser.objects.create(user=user, blocked_user=to_block)
                        messages.success(request, f"{username_to_block} a été bloqué.")
                        return redirect('subscriptions')
                except User.DoesNotExist:
                    messages.error(request, "Cet utilisateur n'existe pas.")
        else:
            form = FollowUserForm(request.POST)
            if form.is_valid():
                username_to_follow = form.cleaned_data['username']
                try:
                    to_follow = User.objects.get(username=username_to_follow)
                    if to_follow == user:
                        messages.error(request, "Tu ne peux pas te suivre toi-même.")
                    elif UserFollows.objects.filter(user=user, followed_user=to_follow).exists():
                        messages.warning(request, f"Tu suis déjà {username_to_follow}.")
                    else:
                        UserFollows.objects.create(user=user, followed_user=to_follow)
                        messages.success(request, f"Tu suis maintenant {username_to_follow}.")
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
    View to unfollow a user.

    - Only accessible via GET request.
    - Deletes the UserFollows relationship between the logged-in user and the given user_id (if it exists).

    Parameters:
    - user_id: ID of the user to unfollow.

    Template:
    - auth/subscriptions.html

    Redirects:
    - To the 'subscriptions' page with a success or error message.
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
    View to unblock a user.

    - Removes the BlockedUser relationship if it exists.

    Parameters:
    - user_id: ID of the user to unblock

    Template:
    - auth/subscriptions.html

    Redirects:
    - To 'subscriptions' with a success or error message
    """

    try:
        to_unblock = User.objects.get(pk=user_id)
        BlockedUser.objects.filter(user=request.user, blocked_user=to_unblock).delete()
        messages.success(request, f"{to_unblock.username} a été débloqué.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")

    return redirect('subscriptions')



@login_required
def block_from_follower_view(request, user_id):
    """
    View to block a user directly from the followers list.

    - Deletes any follow relationship in both directions.
    - Creates a BlockedUser entry if not already blocked.

    Parameters:
    - user_id: ID of the user to block

    Template:
    - auth/subscriptions.html

    Redirects:
    - To the 'subscriptions' page with a success or error message.
    """
    try:
        to_block = User.objects.get(pk=user_id)
        UserFollows.objects.filter(user=request.user, followed_user=to_block).delete()
        UserFollows.objects.filter(user=to_block, followed_user=request.user).delete()
        BlockedUser.objects.get_or_create(user=request.user, blocked_user=to_block)
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