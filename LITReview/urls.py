from django.contrib.auth import views as auth_views
from .forms import CustomPasswordChangeForm
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),

    # UTILISATEUR :
    path('sign_up/', views.signup_view, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('delete_account/', views.delete_account, name='delete_account'),

    path('subscriptions/', views.subscriptions_view, name='subscriptions'),
    path('unfollow/<int:user_id>/', views.unfollow_view, name='unfollow'),
    path('unblock/<int:user_id>/', views.unblock_user_view, name='unblock_user'),
    path('block_follower/<int:user_id>/', views.block_from_follower_view, name='block_from_follower'),

    # FLUX :
    path('flux/', views.flux_view, name='flux'),
    path('ticket/create/', views.create_ticket_view, name='create_ticket'),
    path('review/create/', views.create_ticket_and_review_view, name='create_ticket_review'),
    path('ticket/<int:ticket_id>/review/', views.create_review_response_view, name='create_review_response'),

    # POSTS :
    path('posts/', views.user_posts_view, name='posts'),
    # Modifier / Supprimer tickets:
    path('ticket/<int:ticket_id>/edit/', views.edit_ticket_view, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket_view, name='delete_ticket'),
    # Modifier / Supprimer reviews :
    path('review/<int:review_id>/edit/', views.edit_review_view, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),

    # OUBLI MDP :

    # Formulaire pour saisir l’email : password_reset_form.html
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='auth/password_reset_form.html'),
        name='password_reset'
    ),

    # Confirmation que l’email a été envoyé : password_reset_done.html
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
        name='password_reset_done'
    ),

    # Formulaire pour entrer le nouveau mot de passe après réception de l'email : password_reset_confirm.html
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),

    # Confirmation finale de la réinitialisation et redirection : password_reset_complete.html
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
        name='password_reset_complete'
    ),

    # CHANGEMENT VOLONTAIRE MDP POUR UTILISATEUR CONNECTES:
    # (vue native Django)
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='auth/password_change_form.html',
            form_class=CustomPasswordChangeForm
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'),
        name='password_change_done'
    ),
]


