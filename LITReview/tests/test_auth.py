"""Authentication tests: sign up, login, logout, password reset, access control."""


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthTests(TestCase):
    """Tests automatisés pour l'ensemble des fonctionnalités d'authentification."""

    def setUp(self):
        """Prépare un utilisateur de test pour les scénarios de connexion et de changement de mot de passe."""
        self.user = User.objects.create_user(
            username="alice", email="alice@test.com", password="OldPass123!"
        )

    def test_signup_ok(self):
        """L'utilisateur peut s'inscrire avec un email et un identifiant unique."""
        resp = self.client.post(reverse("sign_up"), {
            "username": "bob",
            "email": "bob@test.com",
            "password1": "NewPass123!",
            "password2": "NewPass123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="bob").exists())

    def test_signup_email_already_used(self):
        """L'inscription échoue si l'email est déjà utilisé par un autre compte."""
        resp = self.client.post(reverse("sign_up"), {
            "username": "another",
            "email": "alice@test.com",  # déjà utilisé par 'alice'
            "password1": "AnotherPass123!",
            "password2": "AnotherPass123!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp, "This email is already used by another account.", status_code=200
        )
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_login_ok(self):
        """Connexion réussie d'un utilisateur avec les bons identifiants."""
        resp = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "OldPass123!"
        })
        self.assertEqual(resp.status_code, 302)

    def test_login_bad_credentials(self):
        """Connexion refusée si le mot de passe ou l'identifiant est incorrect ; message affiché."""
        resp = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "wrong"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "mot de passe invalide", status_code=200)

    def test_logout_redirects(self):
        """Déconnexion de l'utilisateur et redirection vers la page d'accueil."""
        self.client.login(username="alice", password="OldPass123!")
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("home"))

    def test_access_requires_login(self):
        """Le flux (feed) n'est accessible que si l'utilisateur est connecté."""
        resp = self.client.get(reverse("flux"))
        self.assertEqual(resp.status_code, 302)

        self.client.login(username="alice", password="OldPass123!")
        resp = self.client.get(reverse("flux"))
        self.assertEqual(resp.status_code, 200)

    def test_password_change(self):
        """Un utilisateur peut changer son mot de passe et se reconnecter avec le nouveau."""
        self.client.login(username="alice", password="OldPass123!")
        resp = self.client.post(reverse("password_change"), {
            "old_password": "OldPass123!",
            "new_password1": "VeryNew123!",
            "new_password2": "VeryNew123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.client.logout()
        self.assertTrue(self.client.login(username="alice", password="VeryNew123!"))
