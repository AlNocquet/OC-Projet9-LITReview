"""Profile management tests: profile view update, uniqueness rules, and account deletion."""

# Tests du profil utilisateur : mise à jour via la vue, règles d’unicité, suppression de compte.
# Couvre :
# - Mise à jour username/email (succès + redirection) ;
# - Unicité du username (form invalide si déjà pris) ;
# - Unicité de l’email (form invalide si déjà pris) ;
# - Suppression de compte (POST) avec redirection.
#
# Ces tests sont cohérents avec la règle métier : un email ne peut pas être réutilisé par un autre compte.
# Ils supposent la présence d’une validation (formulaire ou modèle) qui refuse un email dupliqué.

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages


class ProfileViewTests(TestCase):
    """Batterie de tests pour la vue 'profile' (consultation / mise à jour) et la suppression de compte."""

    def setUp(self):
        # Prépare deux utilisateurs :
        # - alice : utilisateur connecté pour les tests de modification et suppression
        # - bob   : utilisateur existant afin de tester les conflits d’unicité
        self.alice_password = "Passw0rd!alice"
        self.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=self.alice_password
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password="Passw0rd!bob"
        )

    def test_update_profile_valid(self):
        """
        Mise à jour profil valide :
        - Redirection (302) vers 'profile'
        - Valeurs mises à jour en base
        - Message de succès présent
        """
        self.client.login(username="alice", password=self.alice_password)

        url = reverse("profile")
        payload = {
            "username": "alice_new",
            "email": "alice_new@example.com",
        }

        response = self.client.post(url, data=payload, follow=True)
        self.assertRedirects(response, reverse("profile"))

        self.alice.refresh_from_db()
        self.assertEqual(self.alice.username, "alice_new")
        self.assertEqual(self.alice.email, "alice_new@example.com")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("succès" in str(m).lower() or "mis à jour" in str(m).lower() for m in messages),
            "Un message de succès était attendu après la mise à jour du profil."
        )

    def test_update_profile_username_unique(self):
        """
        Unicité du username :
        - Si le nouveau pseudo existe déjà, la mise à jour échoue (status 200, pas de redirection)
        - Le formulaire contient une erreur sur 'username'
        - Les données en base ne sont pas modifiées
        """
        self.client.login(username="alice", password=self.alice_password)

        url = reverse("profile")
        payload = {
            "username": "bob",              # déjà pris
            "email": "alice@example.com",   # inchangé et propre
        }

        response = self.client.post(url, data=payload)  # pas de follow
        self.assertEqual(response.status_code, 200, "Le template doit être ré-affiché (form invalide).")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("username", form.errors)

        self.alice.refresh_from_db()
        self.assertEqual(self.alice.username, "alice")

    def test_update_profile_email_unique(self):
        """
        Unicité de l’email :
        - Si le nouvel email est déjà utilisé par un autre compte, la mise à jour échoue (status 200)
        - Le formulaire contient une erreur sur 'email'
        - Les données en base ne sont pas modifiées
        """
        self.client.login(username="alice", password=self.alice_password)

        url = reverse("profile")
        payload = {
            "username": "alice",            # inchangé
            "email": "bob@example.com",     # email déjà utilisé par bob
        }

        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 200, "Le template doit être ré-affiché (form invalide).")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("email", form.errors)

        self.alice.refresh_from_db()
        self.assertEqual(self.alice.email, "alice@example.com")

    def test_delete_account(self):
        """
        Suppression de compte :
        - GET renvoie la page de confirmation (200)
        - POST supprime l’utilisateur et redirige vers 'home' (302)
        """
        self.client.login(username="alice", password=self.alice_password)

        url = reverse("delete_account")

        get_resp = self.client.get(url)
        self.assertEqual(get_resp.status_code, 200)

        post_resp = self.client.post(url)
        self.assertRedirects(post_resp, reverse("home"))
        self.assertFalse(
            User.objects.filter(username="alice").exists(),
            "Le compte 'alice' aurait dû être supprimé."
        )