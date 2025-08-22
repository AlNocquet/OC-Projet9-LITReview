"""Social features tests: follow, unfollow, block, and unblock users."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from LITReview.models import UserFollows, BlockedUser


class SocialTests(TestCase):
    def setUp(self):
        """Crée 3 utilisateurs. Alice est connectée par défaut."""
        self.alice = User.objects.create_user("alice", email="alice@test.com", password="Pass123!x")
        self.bob = User.objects.create_user("bob", email="bob@test.com", password="Pass123!x")
        self.carl = User.objects.create_user("carl", email="carl@test.com", password="Pass123!x")
        self.client.login(username="alice", password="Pass123!x")

    # --------------------------------------------------------------------- #
    # Suivre (POST sur /subscriptions/ avec FollowUserForm)
    # --------------------------------------------------------------------- #

    def test_follow_success(self):
        """Alice suit Bob (username exact ou insensible à la casse)."""
        resp = self.client.post(reverse("subscriptions"), {
            "username": "BoB",  # __iexact dans la vue
        })
        # Succès -> redirection vers subscriptions et relation créée
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("subscriptions"))
        self.assertTrue(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists())

    def test_follow_self_forbidden(self):
        """Auto-suivi interdit (message d’erreur, pas de redirection)."""
        resp = self.client.post(reverse("subscriptions"), {
            "username": "alice",
        })
        # Pas de redirection sur erreur : la vue ré-affiche la page
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(UserFollows.objects.filter(user=self.alice, followed_user=self.alice).exists())

    def test_follow_duplicate_forbidden(self):
        """Un même suivi ne peut être créé 2 fois (unique_together respecté côté vue)."""
        UserFollows.objects.create(user=self.alice, followed_user=self.bob)
        resp = self.client.post(reverse("subscriptions"), {
            "username": "bob",
        })
        self.assertEqual(resp.status_code, 200)  # warning + ré-affichage
        self.assertEqual(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).count(), 1)

    def test_follow_forbidden_if_other_blocked_me(self):
        """Impossible de suivre un utilisateur qui m’a bloqué."""
        BlockedUser.objects.create(user=self.bob, blocked_user=self.alice)  # bob a bloqué alice
        resp = self.client.post(reverse("subscriptions"), {"username": "bob"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists())

    def test_follow_forbidden_if_i_blocked_them(self):
        """Impossible de suivre un utilisateur que j’ai bloqué."""
        BlockedUser.objects.create(user=self.alice, blocked_user=self.bob)  # alice a bloqué bob
        resp = self.client.post(reverse("subscriptions"), {"username": "bob"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists())

    # --------------------------------------------------------------------- #
    # Se désabonner (GET /unfollow/<id>/)
    # --------------------------------------------------------------------- #

    def test_unfollow_success(self):
        """Unfollow supprime la relation et redirige vers la page abonnements."""
        UserFollows.objects.create(user=self.alice, followed_user=self.bob)
        resp = self.client.get(reverse("unfollow", args=[self.bob.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("subscriptions"))
        self.assertFalse(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists())

    # --------------------------------------------------------------------- #
    # Bloquer depuis la page abonnements (POST 'block' sur /subscriptions/)
    # --------------------------------------------------------------------- #

    def test_block_from_subscriptions_removes_follows_both_directions_and_creates_block(self):
        """Bloquer via la page abonnements :
        - crée BlockedUser(user=alice, blocked_user=bob)
        - supprime les follow dans les 2 sens (UserFollows)
        - redirige vers subscriptions
        """
        # Suivis dans les 2 sens avant blocage
        UserFollows.objects.create(user=self.alice, followed_user=self.bob)
        UserFollows.objects.create(user=self.bob, followed_user=self.alice)

        resp = self.client.post(reverse("subscriptions"), {
            "block": "1",          # déclenche le BlockUserForm dans la vue
            "username": "bob",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("subscriptions"))

        # Blocage créé
        self.assertTrue(BlockedUser.objects.filter(user=self.alice, blocked_user=self.bob).exists())
        # Suivis supprimés dans les 2 sens
        self.assertFalse(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists())
        self.assertFalse(UserFollows.objects.filter(user=self.bob, followed_user=self.alice).exists())

    # --------------------------------------------------------------------- #
    # Bloquer depuis la liste des followers (GET /block_follower/<id>/)
    # --------------------------------------------------------------------- #

    def test_block_from_follower_endpoint(self):
        """Endpoint dédié : block_from_follower_view (idempotent, supprime les follows)."""
        # Mettons un follow de bob -> alice pour simuler "follower"
        UserFollows.objects.create(user=self.bob, followed_user=self.alice)
        # Alice bloque Bob via l’endpoint dédié
        resp = self.client.get(reverse("block_from_follower", args=[self.bob.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("subscriptions"))

        # Blocage créé
        self.assertTrue(BlockedUser.objects.filter(user=self.alice, blocked_user=self.bob).exists())
        # Suivis supprimés (méthode BlockedUser.block supprime dans les 2 sens)
        self.assertFalse(UserFollows.objects.filter(user=self.alice, followed_user=self.bob).exists())
        self.assertFalse(UserFollows.objects.filter(user=self.bob, followed_user=self.alice).exists())

    # --------------------------------------------------------------------- #
    # Débloquer (GET /unblock/<id>/)
    # --------------------------------------------------------------------- #

    def test_unblock_success(self):
        """Unblock supprime la relation BlockedUser si elle existe (sinon message info) et redirige."""
        BlockedUser.objects.create(user=self.alice, blocked_user=self.bob)
        resp = self.client.get(reverse("unblock_user", args=[self.bob.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("subscriptions"))
        self.assertFalse(BlockedUser.objects.filter(user=self.alice, blocked_user=self.bob).exists())

    # --------------------------------------------------------------------- #
    # Contexte de la page abonnements (GET /subscriptions/)
    # --------------------------------------------------------------------- #

    def test_subscriptions_context_lists(self):
        """La page 'subscriptions' expose bien followed_users / followers / blocked_users dans le contexte."""
        # Prépare des données visibles dans le contexte
        UserFollows.objects.create(user=self.alice, followed_user=self.bob)   # alice suit bob
        UserFollows.objects.create(user=self.carl, followed_user=self.alice)  # carl suit alice
        BlockedUser.objects.create(user=self.alice, blocked_user=self.carl)   # alice bloque carl

        resp = self.client.get(reverse("subscriptions"))
        self.assertEqual(resp.status_code, 200)

        # Le template reçoit ces 3 clés (la vue passe les QuerySets)
        self.assertIn("followed_users", resp.context)
        self.assertIn("followers", resp.context)
        self.assertIn("blocked_users", resp.context)

        # Vérifie le contenu minimal (ids)
        followed_ids = {rel.followed_user_id for rel in resp.context["followed_users"]}
        followers_ids = {rel.user_id for rel in resp.context["followers"]}
        blocked_ids = {rel.blocked_user_id for rel in resp.context["blocked_users"]}

        self.assertIn(self.bob.id, followed_ids)
        self.assertIn(self.carl.id, followers_ids)
        self.assertIn(self.carl.id, blocked_ids)
