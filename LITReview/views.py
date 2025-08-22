from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Value, CharField

from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from itertools import chain

from .models import UserFollows, BlockedUser, Ticket, Review
from .forms import (
    SignUpForm, ProfileUpdateForm, LoginForm, FollowUserForm,
    BlockUserForm, TicketForm, ReviewForm, TicketReviewForm
)


def home_view(request):
    """
    Displays the home page for non-authenticated users.
    Redirects authenticated users to the feed ('flux').
    If the user is already authenticated, they are redirected to the main feed.
    """
    if request.user.is_authenticated:
        return redirect('flux')
    form = LoginForm()
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
            user = form.save()
            login(request, user)
            return redirect('flux')
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
    - POST: Deletes the user's account permanently, logs out the user immediately after deletion, and redirects
        to the home page with a confirmation message.

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
        logout(request)
        user.delete()
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
def user_posts_view(request):
    """
    Displays the authenticated user's own posts (tickets and reviews).

    - Fetches all tickets and reviews created by the user.
    - Annotates each object with a content_type for display logic.
    - Combines and sorts posts in reverse chronological order.

    Template:
    - feed/posts.html
    """
    tickets = Ticket.objects.filter(user=request.user).annotate(content_type=Value('TICKET', output_field=CharField()))
    reviews = Review.objects.filter(user=request.user).annotate(content_type=Value('REVIEW', output_field=CharField()))
    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, 'feed/posts.html', {'posts': posts})


@login_required
def create_ticket_view(request):
    """
    Allows the user to create a new Ticket (review request).

    - GET: display empty form
    - POST: validate and save the new ticket

    Template:
    - feed/form_page.html
    """
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Le ticket a bien été créé.")
            return redirect('flux')
        else:
            messages.error(request, "Erreur : vérifiez le formulaire.")
    else:
        form = TicketForm()
    return render(request, 'feed/form_page.html', {
        'title': "Créer un ticket",
        'form': form,
        'is_ticket': True,
        'has_file': True,
    })


@login_required
def create_review_response_view(request, ticket_id):
    """
    View allowing a user to write a review in response to an existing ticket.

    Parameters:
    - request: HTTP request object
    - ticket_id: ID of the ticket to respond to

    Behavior:
    - GET: displays an empty ReviewForm
    - POST: processes form submission
        - if valid: associates the review with the current user and the ticket, saves it, and redirects to feed
        - if invalid: redisplays the form with error messages

    Access:
    - Only available to authenticated users (login_required)

    Template:
    - feed/form_page.html

    Redirects:
    - Redirects to 'flux' upon successful review creation
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if Review.objects.filter(user=request.user, ticket=ticket).exists():
        messages.warning(request, "Vous avez déjà rédigé une critique pour ce ticket.")
        return redirect('flux')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            messages.success(request, "Votre critique a été publiée.")
            return redirect('flux')
    else:
        form = ReviewForm()
    return render(request, 'feed/form_page.html', {
        'form': form,
        'title': f'Critiquer : {ticket.title}',
        'has_file': False,
        'ticket': ticket,
        'is_review': True,
    })


@login_required
def create_ticket_and_review_view(request):
    """
    View allowing the user to create both a Ticket and an associated Review in a single step.

    Behavior:
    - GET: displays an empty form with fields for both the ticket and the review
    - POST: processes form submission
        - if valid: creates and saves a new Ticket, then creates and saves a Review linked to that ticket
        - if invalid: redisplays the form with error messages

    Access:
    - Only accessible to authenticated users (login_required)

    Template:
    - feed/form_page.html

    Redirects:
    - To 'flux' after successful creation of both objects
    """
    if request.method == 'POST':
        form = TicketReviewForm(request.POST, request.FILES)
        if form.is_valid():
            similar_tickets = Ticket.objects.filter(
                title__iexact=form.cleaned_data['title']
            ).exclude(user=request.user)
            if similar_tickets.exists():
                messages.info(request, "D'autres utilisateurs ont déjà demandé une critique sur ce livre.")
            ticket = Ticket(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                image=form.cleaned_data['image'],
                user=request.user
            )
            ticket.save()
            review = Review(
                headline=form.cleaned_data['headline'],
                body=form.cleaned_data['body'],
                rating=form.cleaned_data['rating'],
                user=request.user,
                ticket=ticket
            )
            review.save()
            messages.success(request, "Le ticket et la critique ont bien été créés.")
            return redirect('flux')
        else:
            messages.error(request, "Erreur : vérifiez les champs du formulaire.")
    else:
        form = TicketReviewForm()
        form.fields['body'].label = "Commentaire"
    return render(request, 'feed/form_page.html', {
        'form': form,
        'title': "Créer une critique",
        'has_file': True,
        'is_review': True,
    })


@login_required
def flux_view(request):
    """
    Vue flux LITReview :
    - Affiche les tickets d'utilisateur courant et des suivis (hors bloqués)
    - Affiche toutes les reviews sur ces tickets (hors bloqués)
    - Affiche les reviews orphelines faites par soi ou ses suivis (hors bloqués) sur tickets non visibles
    - Ordre antéchronologique
    """
    user = request.user
    followed_ids = set(UserFollows.objects.filter(user=user).values_list('followed_user', flat=True))
    blocked_ids = set(BlockedUser.objects.filter(user=user).values_list('blocked_user', flat=True))
    all_tickets = Ticket.objects.filter(
        Q(user=user) | Q(user__in=followed_ids)
    ).exclude(user__in=blocked_ids).order_by('-time_created')
    ticket_blocks = []
    for t in all_tickets:
        reviews = t.review_set.exclude(user__in=blocked_ids).order_by('-time_created')
        t.has_review_by_user = reviews.filter(user=user).exists()
        ticket_blocks.append({
            'kind': 'ticket_block',
            'ticket': t,
            'reviews': list(reviews),
            'time_created': t.time_created,
        })
    visible_authors = (followed_ids | {user.id}) - blocked_ids
    orphan_reviews = Review.objects.filter(
        user__in=visible_authors
    ).exclude(
        ticket__in=all_tickets
    ).exclude(
        user__in=blocked_ids
    ).order_by('-time_created')
    orphan_items = [{
        'kind': 'orphan_review',
        'review': r,
        'time_created': r.time_created,
    } for r in orphan_reviews]
    all_items = sorted(
        ticket_blocks + orphan_items,
        key=lambda it: it['time_created'],
        reverse=True
    )
    return render(request, 'feed/flux.html', {'all_items': all_items})


@login_required
def edit_ticket_view(request, ticket_id):
    """
    View allowing a user to edit one of their own tickets.

    Access:
    - Only accessible to authenticated users (login_required).
    - Only the author of the ticket can edit it.

    Behavior:
    - GET: displays a form pre-filled with the existing ticket data.
    - POST: processes the submitted form to update the ticket.
        - If valid: saves the changes and redirects to 'posts' page.
        - If invalid: redisplays the form with error messages.

    Parameters:
    - request: HTTP request object
    - ticket_id: ID of the ticket to be edited

    Template:
    - feed/form_page.html

    Redirects:
    - To 'posts' or 'flux' after successful modification
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    next_url = request.POST.get('next') or request.GET.get('next') or 'posts'
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre ticket a été modifié avec succès !")
            return redirect(next_url)
        else:
            messages.error(request, "Erreur lors de la modification du ticket.")
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'feed/form_page.html', {
        'form': form,
        'title': 'Modifier le ticket',
        'has_file': True,
        'next': next_url,
    })


@login_required
def delete_ticket_view(request, ticket_id):
    """
    View allowing a user to delete one of their own tickets.

    Access:
    - Only accessible to authenticated users (login_required).
    - Only the author of the ticket can delete it.

    Behavior:
    - GET: displays a confirmation page asking the user to confirm deletion.
    - POST: deletes the ticket and redirects to 'posts' or 'flux' with a success message.

    Parameters:
    - request: HTTP request object
    - ticket_id: ID of the ticket to be deleted

    Template:
    - feed/confirm_delete.html

    Redirects:
    - To 'posts' or 'flux' after successful deletion
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    next_url = request.GET.get('next') or 'posts'
    if request.method == "POST":
        ticket.delete()
        messages.success(request, "Votre ticket a été supprimé avec succès !")
        return redirect(next_url)
    return render(request, 'feed/confirm_delete.html', {
        'ticket': ticket,
        'next': next_url,
    })


@login_required
def edit_review_view(request, review_id):
    """
    View allowing a user to edit one of their own reviews.

    Access:
    - Only accessible to authenticated users (login_required).
    - Only the author of the review can edit it.

    Behavior:
    - GET: displays a form pre-filled with the review's current content.
    - POST: processes submitted form to update the review.
        - If valid: saves changes and redirects to the 'posts' page.
        - If invalid: redisplays the form with error messages.

    Parameters:
    - request: HTTP request object
    - review_id: ID of the review to be edited

    Template:
    - feed/form_page.html

    Redirects:
    - To 'posts' or 'flux' after successful modification
    """
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    next_url = request.POST.get('next') or request.GET.get('next') or 'posts'
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre critique a été modifiée avec succès.")
            return redirect(next_url)
        else:
            messages.error(request, "Erreur lors de la modification de votre critique.")
    else:
        form = ReviewForm(instance=review)
    return render(request, 'feed/form_page.html', {
        'form': form,
        'title': 'Modifier la critique',
        'has_file': False,
        'ticket': review.ticket,
    })


@login_required
def delete_review_view(request, review_id):
    """
    View allowing a user to delete one of their own reviews.

    Access:
    - Only accessible to authenticated users (login_required).
    - Only the author of the review can delete it.

    Behavior:
    - GET: displays a confirmation page asking the user to confirm deletion.
    - POST: deletes the review and redirects to the 'posts' page with a success message.

    Parameters:
    - request: HTTP request object
    - review_id: ID of the review to be deleted

    Template:
    - feed/confirm_delete.html

    Redirects:
    - To 'posts' or 'flux' after successful deletion
    """
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    next_url = request.GET.get('next') or 'posts'
    if request.method == "POST":
        review.delete()
        messages.success(request, "Votre critique a été supprimée avec succès.")
        return redirect(next_url)
    return render(request, 'feed/confirm_delete.html', {
        'object': review,
        'next': next_url,
    })
