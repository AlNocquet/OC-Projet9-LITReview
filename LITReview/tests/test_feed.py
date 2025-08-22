"""Tests du flux utilisateur : affichage, filtrage abonnements/bloqués, tri antéchronologique, bouton critique."""


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from LITReview.models import Ticket, Review, UserFollows, BlockedUser


class FeedTests(TestCase):
    """Tests du flux principal utilisateur (vue 'flux')."""

    def setUp(self):
        # Création des utilisateurs
        self.u1 = User.objects.create_user(username='alice', password='testpass')
        self.u2 = User.objects.create_user(username='bob', password='testpass')
        self.u3 = User.objects.create_user(username='charlie', password='testpass')
        self.u4 = User.objects.create_user(username='zoe', password='testpass')

        # u1 suit u2 et u3
        UserFollows.objects.create(user=self.u1, followed_user=self.u2)
        UserFollows.objects.create(user=self.u1, followed_user=self.u3)
        # u1 bloque u4 (ne verra pas son contenu)
        BlockedUser.objects.create(user=self.u1, blocked_user=self.u4)

        # Tickets : un par utilisateur
        self.t1 = Ticket.objects.create(user=self.u1, title="Ticket U1", description="Desc1")
        self.t2 = Ticket.objects.create(user=self.u2, title="Ticket U2", description="Desc2")
        self.t3 = Ticket.objects.create(user=self.u3, title="Ticket U3", description="Desc3")
        self.t4 = Ticket.objects.create(user=self.u4, title="Ticket U4", description="Desc4")

        # Reviews associées aux tickets
        self.r1 = Review.objects.create(user=self.u1, ticket=self.t2, headline="Critique1", body="Body1", rating=4)
        self.r2 = Review.objects.create(user=self.u2, ticket=self.t1, headline="Critique2", body="Body2", rating=3)
        self.r3 = Review.objects.create(user=self.u3, ticket=self.t2, headline="Critique3", body="Body3", rating=2)
        # Orpheline : critique de u3 sur t4 (ticket de zoe, bloquée)
        self.r4 = Review.objects.create(user=self.u3, ticket=self.t4, headline="Orpheline", body="Body4", rating=5)
        # Review d'un user bloqué (ne doit jamais apparaître dans le flux de u1)
        self.r5 = Review.objects.create(user=self.u4, ticket=self.t2, headline="ParBloqué", body="Body5", rating=1)

        # Authentification sur alice (u1)
        self.client.login(username='alice', password='testpass')

    def test_feed_displays_followed_and_own_content(self):
        """
        Vérifie que le flux montre :
        - les tickets des suivis et de soi,
        - les critiques groupées au bon endroit,
        - les reviews orphelines (y compris sur des tickets d'utilisateurs bloqués, si elles sont écrites par un suivi),
        - aucun contenu écrit PAR un utilisateur bloqué (ni ticket ni review).

        Rappel logique LITReview :
        - Les reviews orphelines d'un suivi sur un ticket d'un bloqué sont visibles (c'est normal).
        - On n'affiche jamais de review ou ticket écrit par un bloqué.
        """
        url = reverse('flux')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        all_items = resp.context['all_items']

        # Tickets visibles (par u1, u2, u3)
        ticket_users = [block['ticket'].user.username
                        for block in all_items if block.get('kind') == 'ticket_block']
        self.assertEqual(set(ticket_users), {'alice', 'bob', 'charlie'})

        # Reviews sur t2 (ticket de bob)
        for block in all_items:
            if block.get('kind') == 'ticket_block' and block['ticket'] == self.t2:
                review_authors = [r.user.username for r in block['reviews']]
                self.assertEqual(set(review_authors), {'alice', 'charlie'})
                self.assertNotIn('zoe', review_authors)  # bloqué

        # Présence de la review orpheline r4 (charlie sur ticket bloqué t4)
        orphans = [item['review'] for item in all_items if item.get('kind') == 'orphan_review']
        self.assertIn(self.r4, orphans)

        # Rien venant de zoe (u4) dans tout le flux
        for item in all_items:
            if item.get('kind') == 'ticket_block':
                self.assertNotEqual(item['ticket'].user, self.u4)
                for r in item['reviews']:
                    self.assertNotEqual(r.user, self.u4)
            if item.get('kind') == 'orphan_review':
                self.assertNotEqual(item['review'].user, self.u4)

        def test_feed_order_is_reverse_chronological(self):
            """
            Vérifie que le flux est trié antéchronologiquement (du plus récent au plus ancien).
            """
            url = reverse('flux')
            resp = self.client.get(url)
            all_items = resp.context['all_items']
            times = [item['time_created'] for item in all_items]
            self.assertEqual(times, sorted(times, reverse=True))

        def test_review_button_visibility(self):
            """
            Vérifie la visibilité du bouton "Critiquer" sur chaque ticket :
            - présent si l'utilisateur n'a PAS déjà critiqué,
            - absent sinon (has_review_by_user).
            """
            url = reverse('flux')
            resp = self.client.get(url)
            all_items = resp.context['all_items']
            for block in all_items:
                if block.get('kind') == 'ticket_block':
                    ticket = block['ticket']
                    if ticket == self.t2:
                        self.assertTrue(ticket.has_review_by_user)
                    if ticket == self.t3:
                        self.assertFalse(ticket.has_review_by_user)
