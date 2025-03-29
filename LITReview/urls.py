
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views



urlpatterns = [
    path('', views.home_view, name='home'),

    # GESTION UTILISATEUR :
    path('sign_up/', views.signup_view, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('delete_account/', views.delete_account, name='delete_account'),


    path('flux/', views.flux_view, name='flux'),

    
    
    
    # Mot de passe oublié :

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