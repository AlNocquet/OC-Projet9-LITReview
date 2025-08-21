"""Unit tests for models: Ticket, Review, UserFollows, BlockedUser."""

# Tests unitaires des modèles : Ticket, Review, UserFollows, BlockedUser.

# Spécificités prises en compte :
# - Les validateurs de champs Django (ex : Min/Max validators) ne sont exécutés que si l'on appelle .full_clean() sur l'instance (ou via un ModelForm).
# On les teste donc avec .full_clean() et on attend ValidationError.
# - Les contraintes d'unicité (unique_together) sont gérées par la DB : on vérifie IntegrityError lors d'une double insertion.
# - La méthode de classe BlockedUser.block() doit supprimer les follows dans les deux sens et créer (ou récupérer) la relation de blocage (idempotente).


from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from LITReview.models import Ticket, Review, UserFollows, BlockedUser


class TicketModelTests(TestCase):
    def test_create_ticket_minimal_valid(self):
        """Création d'un ticket valide (tous champs requis présents)."""
        user = User.objects.create_user(username="alice", password="pass")
        t = Ticket.objects.create(title="Livre A", description="Demande", user=user)
        self.assertEqual(t.title, "Livre A")
        self.assertEqual(t.user.username, "alice")
        self.assertIsNotNone(t.time_created)

    def test_ticket_reverse_relation_to_reviews(self):
        """La relation inverse ticket.review_set fonctionne correctement."""
        user = User.objects.create_user(username="bob", password="pass")
        t = Ticket.objects.create(title="Livre B", description="Desc", user=user)
        r = Review.objects.create(
            rating=3, headline="Ok", body="Contenu", user=user, ticket=t
        )
        self.assertIn(r, t.review_set.all())


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="carol", password="pass")
        self.ticket = Ticket.objects.create(
            title="Livre C", description="Desc", user=self.user
        )

    def test_create_valid_review(self):
        """Création d'une review valide (rating dans [0..5])."""
        r = Review.objects.create(
            rating=4, headline="Bon livre", body="Super", user=self.user, ticket=self.ticket
        )
        self.assertEqual(r.rating, 4)
        self.assertEqual(r.user, self.user)
        self.assertEqual(r.ticket, self.ticket)

    def test_rating_too_high_raises_validation_error(self):
        """
        Les validateurs Min/Max s'appliquent via full_clean() :
        rating=6 doit lever ValidationError.
        """
        r = Review(
            rating=6, headline="Trop haut", body="X", user=self.user, ticket=self.ticket
        )
        with self.assertRaises(ValidationError):
            r.full_clean()  # déclenche Min/Max validators

    def test_rating_too_low_raises_validation_error(self):
        """rating=-1 doit lever ValidationError via full_clean()."""
        r = Review(
            rating=-1, headline="Trop bas", body="X", user=self.user, ticket=self.ticket
        )
        with self.assertRaises(ValidationError):
            r.full_clean()

    def test_body_is_required(self):
        """body est requis (blank=False) → ValidationError si vide."""
        r = Review(
            rating=2, headline="Titre", body="", user=self.user, ticket=self.ticket
        )
        with self.assertRaises(ValidationError):
            r.full_clean()


class UserFollowsModelTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.bob = User.objects.create_user(username="bob", password="pass")

    def test_follow_once(self):
        """Un utilisateur peut suivre un autre (création simple)."""
        rel = UserFollows.objects.create(user=self.alice, followed_user=self.bob)
        self.assertEqual(rel.user, self.alice)
        self.assertEqual(rel.followed_user, self.bob)
        # Vérifie les related_name :
        self.assertIn(rel, self.alice.following.all())
        self.assertIn(rel, self.bob.followed_by.all())

    def test_unique_constraint_user_followed_user(self):
        """
        unique_together('user','followed_user') : impossible de créer deux fois
        le même couple → IntegrityError.
        """
        UserFollows.objects.create(user=self.alice, followed_user=self.bob)
        with self.assertRaises(IntegrityError):
            UserFollows.objects.create(user=self.alice, followed_user=self.bob)


class BlockedUserModelTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.bob = User.objects.create_user(username="bob", password="pass")

    def test_str_representation(self):
        """__str__ doit renvoyer 'alice a bloqué bob' (selon implémentation)."""
        blk = BlockedUser.objects.create(user=self.alice, blocked_user=self.bob)
        self.assertEqual(str(blk), "alice a bloqué bob")

    def test_block_method_removes_mutual_follows_and_creates_block(self):
        """
        BlockedUser.block(user, target) :
        - supprime les relations de follow dans les deux sens,
        - crée la relation de blocage (idempotente).
        """
        # Crée des follows dans les deux sens
        UserFollows.objects.create(user=self.alice, followed_user=self.bob)
        UserFollows.objects.create(user=self.bob, followed_user=self.alice)

        # Bloque
        BlockedUser.block(self.alice, self.bob)

        # Follows supprimés dans les deux sens
        self.assertFalse(
            UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists()
        )
        self.assertFalse(
            UserFollows.objects.filter(user=self.bob, followed_user=self.alice).exists()
        )

        # Blocage bien présent
        self.assertTrue(
            BlockedUser.objects.filter(user=self.alice, blocked_user=self.bob).exists()
        )

        # Idempotence : re-bloquer ne crée pas de doublon
        BlockedUser.block(self.alice, self.bob)
        self.assertEqual(
            BlockedUser.objects.filter(user=self.alice, blocked_user=self.bob).count(), 1
        )

    def test_blocked_user_unique_constraint(self):
        """unique_together('user','blocked_user') : pas de doublon possible."""
        BlockedUser.objects.create(user=self.alice, blocked_user=self.bob)
        with self.assertRaises(IntegrityError):
            BlockedUser.objects.create(user=self.alice, blocked_user=self.bob)