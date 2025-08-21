"""Authentication tests: sign up, login, logout, password reset, access control."""

# test_signup_ok : succès d’inscription unique
# test_signup_email_already_used : refus si email déjà pris (nouveau depuis ta dernière évolution)
# test_login_ok : succès de connexion
# test_login_bad_credentials : refus de connexion + message d’erreur affiché
# test_logout_redirects : logout et redirection
# test_access_requires_login : protection des vues privées
# test_password_change : changement du mot de passe

## Ces tests couvrent tout le cycle : inscription → connexion → accès protégé → déconnexion → changement de mot de passe → sécurité et messages utilisateur.


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthTests(TestCase):
    def setUp(self):
        # Create initial user for login and password change tests
        self.user = User.objects.create_user(username="alice", email="alice@test.com", password="OldPass123!")

    def test_signup_ok(self):
        """Test that a user can sign up with a unique email and username."""
        resp = self.client.post(reverse("sign_up"), {
            "username": "bob",
            "email": "bob@test.com",
            "password1": "NewPass123!",
            "password2": "NewPass123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="bob").exists())

    def test_signup_email_already_used(self):
        """Test that signup is refused if email is already used."""
        resp = self.client.post(reverse("sign_up"), {
            "username": "another",
            "email": "alice@test.com",  # Already used by 'alice'
            "password1": "AnotherPass123!",
            "password2": "AnotherPass123!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "This email is already used by another account.", status_code=200)
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_login_ok(self):
        """Test that an existing user can log in with correct credentials."""
        resp = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "OldPass123!"
        })
        self.assertEqual(resp.status_code, 302)

    def test_login_bad_credentials(self):
        """Test that login fails with incorrect password or username and shows error."""
        resp = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "wrong"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "mot de passe invalide", status_code=200)

    def test_logout_redirects(self):
        """Test that logout redirects to home page."""
        self.client.login(username="alice", password="OldPass123!")
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("home"))

    def test_access_requires_login(self):
        """Test that the feed page is inaccessible without login and accessible when logged in."""
        resp = self.client.get(reverse("flux"))
        self.assertEqual(resp.status_code, 302)
        self.client.login(username="alice", password="OldPass123!")
        resp = self.client.get(reverse("flux"))
        self.assertEqual(resp.status_code, 200)

    def test_password_change(self):
        """Test that a user can change password and log in with the new one."""
        self.client.login(username="alice", password="OldPass123!")
        resp = self.client.post(reverse("password_change"), {
            "old_password": "OldPass123!",
            "new_password1": "VeryNew123!",
            "new_password2": "VeryNew123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.client.logout()
        self.assertTrue(self.client.login(username="alice", password="VeryNew123!"))