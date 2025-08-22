"""CRUD Reviews : création (2 parcours), contrainte 1 review/ticket/utilisateur,
édition/suppression et contrôles d'accès."""


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from LITReview.models import Ticket, Review


class ReviewTests(TestCase):
    def setUp(self):
        # Utilisateurs de test
        self.alice = User.objects.create_user(
            username="alice", email="alice@test.com", password="Pass1234!"
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@test.com", password="Pass1234!"
        )

        # Ticket de bob (servira pour 'répondre à un ticket')
        self.ticket_bob = Ticket.objects.create(
            title="Dune",
            description="Demande de critique",
            user=self.bob,
        )

    def test_create_ticket_and_review_ok(self):
        """
        Parcours 'Créer une critique' : crée un Ticket + une Review d'un coup.
        - POST /review/create/
        - Redirige vers 'flux'
        - Crée 1 ticket (auteur courant) et 1 review liée
        """
        # Connexion d'alice
        self.client.login(username="alice", password="Pass1234!")

        # Données du formulaire combiné (TicketReviewForm)
        payload = {
            # Champs ticket
            "title": "1984",
            "description": "Je publie un ticket + critique en une étape.",
            # Pas d'image (facultative)
            # Champs review
            "headline": "Chef-d'œuvre",
            "body": "Texte argumenté.",
            "rating": 5,
        }

        resp = self.client.post(reverse("create_ticket_review"), data=payload)
        # Doit rediriger vers le flux si succès
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("flux"))

        # Vérifications DB
        self.assertEqual(Ticket.objects.count(), 2)   # ticket_bob + nouveau ticket d'alice
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.first()
        self.assertEqual(review.user, self.alice)       # auteur de la review = alice
        self.assertEqual(review.ticket.user, self.alice)  # ticket créé par alice (form combiné)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.headline, "Chef-d'œuvre")

    def test_create_review_response_once_per_user(self):
        """
        Parcours 'Répondre à un ticket' : 1 seule review par utilisateur et par ticket.
        - 1er POST /ticket/<id>/review/ : OK, création
        - 2e POST sur le même ticket : redirection vers 'flux', aucune review supplémentaire
        """
        self.client.login(username="alice", password="Pass1234!")

        url = reverse("create_review_response", args=[self.ticket_bob.id])

        # 1er envoi : création OK
        payload_ok = {
            "headline": "Intéressant",
            "body": "Un univers riche.",
            "rating": 4,
        }
        resp1 = self.client.post(url, data=payload_ok)
        self.assertEqual(resp1.status_code, 302)
        self.assertRedirects(resp1, reverse("flux"))
        self.assertEqual(Review.objects.filter(ticket=self.ticket_bob, user=self.alice).count(), 1)

        # 2e envoi : doit être refusé (vue renvoie redirect 'flux' avec message)
        payload_dup = {
            "headline": "Doublon",
            "body": "Je tente une 2e critique.",
            "rating": 3,
        }
        resp2 = self.client.post(url, data=payload_dup)
        self.assertEqual(resp2.status_code, 302)
        self.assertRedirects(resp2, reverse("flux"))
        # Toujours une seule review pour (alice, ticket_bob)
        self.assertEqual(Review.objects.filter(ticket=self.ticket_bob, user=self.alice).count(), 1)

    def test_edit_and_delete_review_permissions(self):
        """
        Édition/Suppression d'une review :
        - L'auteur peut modifier puis supprimer (redirige et enlève de la DB)
        - Un autre utilisateur ne peut ni modifier ni supprimer (404 via get_object_or_404)
        """
        # Créons d'abord une review d'alice sur le ticket de bob
        review = Review.objects.create(
            user=self.alice,
            ticket=self.ticket_bob,
            headline="Première version",
            body="Contenu initial.",
            rating=3,
        )

        # 1) Bob (non auteur) → EDIT interdit (404)
        self.client.login(username="bob", password="Pass1234!")
        resp_forbidden_edit = self.client.post(
            reverse("edit_review", args=[review.id]),
            data={"headline": "Hack", "body": "Essai d'édition", "rating": 2},
        )
        self.assertEqual(resp_forbidden_edit.status_code, 404)

        # 2) Bob (non auteur) → DELETE interdit (404)
        resp_forbidden_delete = self.client.post(
            reverse("delete_review", args=[review.id])
        )
        self.assertEqual(resp_forbidden_delete.status_code, 404)

        # 3) Alice (auteur) → EDIT autorisé
        self.client.login(username="alice", password="Pass1234!")
        resp_edit = self.client.post(
            reverse("edit_review", args=[review.id]),
            data={"headline": "Version modifiée", "body": "Texte mis à jour", "rating": 5},
        )
        # Redirection vers 'posts' par défaut (voir vue)
        self.assertEqual(resp_edit.status_code, 302)
        self.assertIn(resp_edit.url, [reverse("posts"), reverse("flux")])

        # Reload et vérifications
        review.refresh_from_db()
        self.assertEqual(review.headline, "Version modifiée")
        self.assertEqual(review.rating, 5)

        # 4) Alice (auteur) → DELETE autorisé
        resp_delete = self.client.post(reverse("delete_review", args=[review.id]))
        self.assertEqual(resp_delete.status_code, 302)
        self.assertIn(resp_delete.url, [reverse("posts"), reverse("flux")])
        self.assertFalse(Review.objects.filter(id=review.id).exists())
