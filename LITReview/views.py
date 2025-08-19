from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Value, CharField

from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from itertools import chain

from .models import UserFollows, BlockedUser, Ticket, Review
from .forms import SignUpForm, ProfileUpdateForm, LoginForm, FollowUserForm, BlockUserForm, TicketForm, ReviewForm, TicketReviewForm


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
                # infos ne venant pas du formulaire mais doivent être ajoutées côté serveur (user)
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
        'is_ticket': True, # déclencher l’inclusion CSS > Formulaire différent de ceux de connexion, etc.
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
        # l'utilisateur ne peut poster qu'une critique par ticket via l'url directe , si le .exists() est False, on peut reposter.
        messages.warning(request, "Vous avez déjà rédigé une critique pour ce ticket.") 
            # Btn enlevé mais si user tente /ticket/ticket_id/review/ → warning
        return redirect('flux')
     
    ticket = get_object_or_404(Ticket, pk=ticket_id)

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
        'ticket': ticket,  # Ticket au dessus
        'is_review': True,  # Flag dans le template
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
    Displays the main feed for the authenticated user.

    Access:
    - Only accessible to authenticated users (login_required).

    Behavior:
    - Displays tickets and reviews from followed users AND from the user themselves,
      excluding those from blocked users.
    - Groups each ticket with its associated reviews (reviews for the ticket displayed above),
      with each block sorted in a globally reverse chronological order.
    - Also displays orphan reviews (whose ticket is not visible) at the correct chronological position.

    Details:
    - Tickets and reviews are merged into a single homogeneous list,
      each element being either a "ticket+reviews block" or an "orphan review."
    - The feed thus allows users to view, in order, all relevant activity (tickets, reviews)
      from followed people, while respecting privacy/blocking rules.

    Template:
    - feed/flux.html

    Context:
    - all_items: list of blocks to be rendered in the template.
    """

    user = request.user 
        # Request : objet Django avec infos sur la requête en cours (URL, méthode, session, etc.)
        # > @login_required, jamais AnonymousUser;

    # 1. Récupérer les IDs des utilisateurs suivis :
    followed_ids = set(
        UserFollows.objects.filter(user=user).values_list('followed_user', flat=True)
    )
        # flat=True pour aplatir le tuple en liste simple [2, 5, 7] au lieu de [(2,), (5,), (7,)] ;
        # set(...) convertit en ensemble élément uniques {2, 5, 7} 
            # > éviter les doublons + faciliter les opérations ensemblistes.

    # 2. Récupérer les IDs des utilisateurs bloqués
    blocked_ids = set(
        BlockedUser.objects.filter(user=user).values_list('blocked_user', flat=True)
    )    

    # 3. Construire la liste des auteurs visibles (moi + suivis - bloqués)
    visible_authors = (followed_ids | {user.id}) - blocked_ids
        # | -> union (OU ensembliste) : les ids suivis + id de l’utilisateur

    # 4. Tickets visibles (auteurs visibles uniquement)
    visible_tickets = Ticket.objects.filter(user__in=visible_authors).order_by('-time_created')
        # QuerySet de Tickets visibles créés par moi ou mes suivis, triés par date décroissante

    # 5. Blocs ticket + reviews associées (reviews = postées par auteurs visibles)
    ticket_blocks = []  
        # liste blocs {ticket + reviews}

    for t in visible_tickets:
        r_qs = t.review_set.filter(user__in=visible_authors).order_by('-time_created')
            # QuerySet Reviews visibles pour le ticket, tris décroissant
            # review_set : généré automatiquement par Django, relation inverse entre Ticket et Review
        t.has_review_by_user = r_qs.filter(user=user).exists() 
            # chaque objet ticket un attribut has_review_by_user (booléen)
            # > Vérifie si a déjà critiqué ce ticket (bouton “Critiquer” : show_critic_button True/False template)

            # Chaque élément de la liste ticket_blocks est un dictionnaire, pas de SQL
        ticket_blocks.append({
            'kind': 'ticket_block',   # étiquette de type
            'ticket': t,              # objet Ticket (avec tous ses champs)
            'reviews': list(r_qs),    # Convertion en liste Python d’objets Review (venant du QuerySet r_qs)
            'time_created': t.time_created,  # clé de tri globale = date du ticket
        })


    # 6. Reviews orphelines (critiques des auteurs visibles, mais dont le ticket n'est pas visible)
    orphan_reviews = Review.objects.filter(user__in=visible_authors).exclude(ticket__in=visible_tickets).order_by('-time_created')
        # Reviews orphelines = critiques de mes suivis dont le ticket n’est PAS visible (auteur Ticket non suivi)

    # Boucle de list comprehension avec dictionnaires
    orphan_items = [{
            'kind': 'orphan_review', # étiquette de type
            'review': r, # l’objet Review complet (avec tous ses champs)
            'time_created': r.time_created,  # clé de tri globale = date de la review
        } for r in orphan_reviews] 
            # une seule boucle, un seul tri, un seul type de structure (homogène avec ticket_blocks) pour template


    # 7. Fusionner tous les items et trier antéchronologiquement
    all_items = sorted(ticket_blocks + orphan_items, key=lambda it: it['time_created'], reverse=True)
        #  Pour chaque élément it de la liste, prends sa valeur it['time_created'] comme clé de tri et ordonne du plus récent au plus ancien

    # 8. Renvoyer au template
    return render(request, 'feed/flux.html', {
        'all_items': all_items
    })



def edit_ticket_view(request, ticket_id): # convention de nommage automatique, Django lit l’URL (path)
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
        # (primary K=ticket_id, user=request.user) → “je le cherche par ID, mais seulement s’il m’appartient”.
    next_url = request.POST.get('next') or request.GET.get('next') or 'posts'
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
            # form = TicketForm(instance=ticket) → “je veux modifier ce ticket-là”
        if form.is_valid(): # combinant les contraintes du Model et du Form
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
    'ticket': review.ticket, # Ticket au dessus
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

