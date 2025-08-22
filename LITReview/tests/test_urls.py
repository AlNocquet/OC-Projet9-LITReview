"""URL tests: reverse & resolve for all named routes; public vs protected access."""

# test_public_urls_resolve_and_status : public routes resolve and return 200/302
# test_protected_urls_redirect_when_anonymous : protected routes redirect to login if not logged in
# test_protected_urls_access_when_logged_in : protected routes return 200/302 for logged user
# test_password_reset_urls_resolve : Django password reset routes resolve
# test_password_change_urls_resolve_and_access : Django password change routes resolve and enforce access


from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views

from LITReview import views
from LITReview.models import Ticket, Review


class UrlsTests(TestCase):
    def setUp(self):
        # Users + one ticket/review for id-based routes
        self.alice = User.objects.create_user(username="alice", email="a@a.a", password="Pass1234!")
        self.bob = User.objects.create_user(username="bob", email="b@b.b", password="Pass1234!")

        self.ticket_alice = Ticket.objects.create(title="T1", description="d", user=self.alice)
        self.review_alice = Review.objects.create(
            user=self.alice, ticket=self.ticket_alice, headline="H", body="B", rating=4
        )

    # ----------------------------
    # Public routes
    # ----------------------------
    def test_public_urls_resolve_and_status(self):
        url = reverse("home")
        self.assertEqual(resolve(url).func, views.home_view)
        self.assertEqual(self.client.get(url).status_code, 200)

        url = reverse("sign_up")
        self.assertEqual(resolve(url).func, views.signup_view)
        self.assertEqual(self.client.get(url).status_code, 200)

        url = reverse("login")
        self.assertEqual(resolve(url).func, views.login_view)
        self.assertEqual(self.client.get(url).status_code, 200)

        url = reverse("logout")
        self.assertEqual(resolve(url).func, views.logout_view)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("home"))

    # ----------------------------
    # Protected routes (anonymous)
    # ----------------------------
    def test_protected_urls_redirect_when_anonymous(self):
        protected_redirect = [
            ("profile", (), views.profile_view),
            ("delete_account", (), views.delete_account),
            ("subscriptions", (), views.subscriptions_view),
            ("flux", (), views.flux_view),
            ("create_ticket", (), views.create_ticket_view),
            ("create_ticket_review", (), views.create_ticket_and_review_view),
            ("posts", (), views.user_posts_view),
            ("edit_review", (self.review_alice.id,), views.edit_review_view),
            ("delete_review", (self.review_alice.id,), views.delete_review_view),
            ("create_review_response", (self.ticket_alice.id,), views.create_review_response_view),
            ("unfollow", (self.bob.id,), views.unfollow_view),
            ("unblock_user", (self.bob.id,), views.unblock_user_view),
            ("block_from_follower", (self.bob.id,), views.block_from_follower_view),
            ("edit_ticket", (self.ticket_alice.id,), views.edit_ticket_view),
            ("delete_ticket", (self.ticket_alice.id,), views.delete_ticket_view),
        ]
        for name, args, view_func in protected_redirect:
            url = reverse(name, args=args)
            self.assertEqual(resolve(url).func, view_func)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, msg=f"{name} should redirect for anonymous")

    # ----------------------------
    # Protected routes (logged in)
    # ----------------------------
    def test_protected_urls_access_when_logged_in(self):
        self.client.login(username="alice", password="Pass1234!")

        ok_routes = [
            ("profile", (), views.profile_view),
            ("delete_account", (), views.delete_account),
            ("subscriptions", (), views.subscriptions_view),
            ("flux", (), views.flux_view),
            ("create_ticket", (), views.create_ticket_view),
            ("create_ticket_review", (), views.create_ticket_and_review_view),
            ("posts", (), views.user_posts_view),
            ("edit_ticket", (self.ticket_alice.id,), views.edit_ticket_view),
            ("delete_ticket", (self.ticket_alice.id,), views.delete_ticket_view),
            ("edit_review", (self.review_alice.id,), views.edit_review_view),
            ("delete_review", (self.review_alice.id,), views.delete_review_view),
            ("create_review_response", (self.ticket_alice.id,), views.create_review_response_view),
        ]
        for name, args, view_func in ok_routes:
            url = reverse(name, args=args)
            self.assertEqual(resolve(url).func, view_func)
            resp = self.client.get(url)
            if name == "create_review_response":
                # Alice already has a review on her ticket → redirect flux
                self.assertEqual(resp.status_code, 302)
                self.assertRedirects(resp, reverse("flux"))
            else:
                self.assertEqual(resp.status_code, 200, msg=f"{name} should be 200 for logged user")

        for name, args, view_func in [
            ("unfollow", (self.bob.id,), views.unfollow_view),
            ("unblock_user", (self.bob.id,), views.unblock_user_view),
            ("block_from_follower", (self.bob.id,), views.block_from_follower_view),
        ]:
            url = reverse(name, args=args)
            self.assertEqual(resolve(url).func, view_func)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(resp, reverse("subscriptions"))

    # ----------------------------
    # Password reset routes
    # ----------------------------
    def test_password_reset_urls_resolve(self):
        self.assertEqual(resolve(reverse("password_reset")).func.view_class, auth_views.PasswordResetView)
        self.assertEqual(resolve(reverse("password_reset_done")).func.view_class, auth_views.PasswordResetDoneView)
        url = reverse("password_reset_confirm", kwargs={"uidb64": "uid", "token": "set-password"})
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetConfirmView)
        self.assertEqual(
            resolve(reverse("password_reset_complete")).func.view_class,
            auth_views.PasswordResetCompleteView
        )

    # ----------------------------
    # Password change routes
    # ----------------------------
    def test_password_change_urls_resolve_and_access(self):
        self.assertEqual(resolve(reverse("password_change")).func.view_class, auth_views.PasswordChangeView)
        self.assertEqual(resolve(reverse("password_change_done")).func.view_class, auth_views.PasswordChangeDoneView)

        resp = self.client.get(reverse("password_change"))
        self.assertEqual(resp.status_code, 302)

        self.client.login(username="alice", password="Pass1234!")
        resp = self.client.get(reverse("password_change"))
        self.assertEqual(resp.status_code, 200)
