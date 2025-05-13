
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views



urlpatterns = [
    path('', views.home_view, name='home'),
    
    # FLUX :
    path('flux/', views.flux_view, name='flux'),

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


    # OUBLI MDP :

    # Formulaire pour saisir l’email : password_reset_form.html
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html'
    ), name='password_reset'),

    # Confirmation que l’email a été envoyé : password_reset_done.html
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),

    # Formulaire pour entrer le nouveau mot de passe : password_reset_confirm.html
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    # Confirmation finale de la réinitialisation et redirection : password_reset_complete.html
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]