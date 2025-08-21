"""Profile form tests: update constraints and email uniqueness validation."""

# Tests unitaires du formulaire de mise à jour de profil (ProfileUpdateForm).
# Couvre :
# - Mise à jour valide username/email ;
# - Unicité du username (form invalide si déjà pris) ;
# - Unicité de l’email (form invalide si déjà pris).
#
# Ces tests reflètent la règle : un email ne peut pas être utilisé par deux comptes.

from django.test import TestCase
from django.contrib.auth.models import User
from LITReview.forms import ProfileUpdateForm


class ProfileUpdateFormTests(TestCase):
    """Batterie de tests pour le formulaire 'ProfileUpdateForm'."""

    def setUp(self):
        # Prépare deux utilisateurs :
        # - alice : instance utilisée comme instance=... à mettre à jour
        # - bob   : collision attendue pour les tests d’unicité username/email
        self.user1 = User.objects.create_user(
            username="alice", email="alice@example.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            username="bob", email="bob@example.com", password="password123"
        )

    def test_update_username_email_ok(self):
        """
        Mise à jour valide :
        - Le formulaire est valide avec un username et un email inédits
        - Les valeurs sont correctement enregistrées par save()
        """
        form = ProfileUpdateForm(
            data={"username": "alice_new", "email": "new_email@example.com"},
            instance=self.user1,
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated_user = form.save()
        self.assertEqual(updated_user.username, "alice_new")
        self.assertEqual(updated_user.email, "new_email@example.com")

    def test_update_username_duplicate_refused(self):
        """
        Unicité du username :
        - Si le username fourni correspond à un autre compte, le formulaire est invalide
        - Une erreur est présente sur le champ 'username'
        """
        form = ProfileUpdateForm(
            data={"username": "bob", "email": "alice_new@example.com"},
            instance=self.user1,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_update_email_duplicate_refused(self):
        """
        Unicité de l’email :
        - Si l’email fourni correspond à un autre compte, le formulaire est invalide
        - Une erreur est présente sur le champ 'email'
        """
        form = ProfileUpdateForm(
            data={"username": "alice_new", "email": "bob@example.com"},  # email déjà utilisé par user2
            instance=self.user1,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)