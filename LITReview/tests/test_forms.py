"""Unit tests for forms: authentication, profile, social, ticket, and review."""

from django.test import TestCase
from django.contrib.auth.models import User

from LITReview.forms import (
    SignUpForm, LoginForm, ProfileUpdateForm,
    FollowUserForm, BlockUserForm,
    TicketForm, ReviewForm, TicketReviewForm
)


class SignUpFormTests(TestCase):
    def test_valid_signup(self):
        """SignUpForm → valide avec username/email/mots de passe OK."""
        form = SignUpForm(data={
            'username': 'alice',
            'email': 'alice@test.com',
            'password1': 'ComplexPwd123',
            'password2': 'ComplexPwd123'
        })
        self.assertTrue(form.is_valid())

    def test_username_already_exists(self):
        """SignUpForm → invalide si username déjà pris (unicité User.username)."""
        User.objects.create_user(username='alice', password='pass')
        form = SignUpForm(data={
            'username': 'alice',
            'email': 'alice@test.com',
            'password1': 'ComplexPwd123',
            'password2': 'ComplexPwd123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class LoginFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass')

    def test_valid_login(self):
        """LoginForm (AuthenticationForm) → valide avec bons identifiants."""
        form = LoginForm(data={'username': 'bob', 'password': 'pass'})
        self.assertTrue(form.is_valid())

    def test_invalid_login(self):
        """LoginForm → invalide avec mauvais mot de passe."""
        form = LoginForm(data={'username': 'bob', 'password': 'wrong'})
        self.assertFalse(form.is_valid())


class ProfileUpdateFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='bob', email='bob@test.com', password='pass'
        )

    def test_valid_update(self):
        """ProfileUpdateForm → valide avec username/email modifiés."""
        form = ProfileUpdateForm(
            data={'username': 'bob2', 'email': 'bob2@test.com'},
            instance=self.user
        )
        self.assertTrue(form.is_valid())

    def test_username_already_exists_on_update(self):
        """
        ProfileUpdateForm → invalide si username dupliqué.
        (Email n’est pas vérifié pour unicité dans le form.)
        """
        User.objects.create_user(username='alice', email='alice@test.com', password='pass')
        form = ProfileUpdateForm(
            data={'username': 'alice', 'email': 'bob@test.com'},
            instance=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class FollowBlockFormsTests(TestCase):
    """
    IMPORTANT :
    - FollowUserForm / BlockUserForm ne valident PAS l’existence d’un utilisateur.
      La vérification est gérée dans la vue (subscriptions_view).
    - Ici, on teste uniquement la validation de champ et la récupération de la donnée.
    """

    def test_follow_form_simple_validation(self):
        form = FollowUserForm(data={'username': 'unknown'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'unknown')

    def test_follow_form_with_existing_username(self):
        User.objects.create_user(username='alice', password='pass')
        form = FollowUserForm(data={'username': 'alice'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'alice')

    def test_block_form_simple_validation(self):
        form = BlockUserForm(data={'username': 'someone'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'someone')

    def test_block_form_with_existing_username(self):
        User.objects.create_user(username='charles', password='pass')
        form = BlockUserForm(data={'username': 'charles'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'charles')


class TicketFormTests(TestCase):
    def test_valid_ticket(self):
        """TicketForm → valide avec titre/description ; image optionnelle."""
        form = TicketForm(data={'title': 'Titre', 'description': 'Texte'})
        self.assertTrue(form.is_valid())

    def test_invalid_ticket_no_title(self):
        """TicketForm → invalide si titre vide (obligatoire)."""
        form = TicketForm(data={'title': '', 'description': 'Texte'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_ticket_no_description(self):
        """TicketForm → invalide si description manquante (obligatoire côté modèle)."""
        form = TicketForm(data={'title': 'Un titre'})
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)


class ReviewFormTests(TestCase):
    def test_valid_review(self):
        """ReviewForm → valide avec rating ∈ [0;5]."""
        form = ReviewForm(data={'headline': 'Super', 'rating': 4, 'body': 'Texte'})
        self.assertTrue(form.is_valid())

    def test_invalid_review_rating_too_high(self):
        """ReviewForm → invalide si rating > 5 (validators modèle)."""
        form = ReviewForm(data={'headline': 'Oops', 'rating': 6, 'body': 'Texte'})
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_invalid_review_rating_negative(self):
        """ReviewForm → invalide si rating < 0 (validators modèle)."""
        form = ReviewForm(data={'headline': 'Oops', 'rating': -1, 'body': 'Texte'})
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_invalid_review_missing_headline(self):
        """ReviewForm → invalide si titre manquant (obligatoire)."""
        form = ReviewForm(data={'headline': '', 'rating': 3, 'body': 'Texte'})
        self.assertFalse(form.is_valid())
        self.assertIn('headline', form.errors)

    def test_invalid_review_missing_body(self):
        """ReviewForm → invalide si texte manquant (obligatoire côté formulaire)."""
        form = ReviewForm(data={'headline': 'Titre', 'rating': 3, 'body': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)


class TicketReviewFormTests(TestCase):
    def test_valid_ticket_and_review(self):
        """
        TicketReviewForm → valide si tous les champs requis (image facultative).
        """
        form = TicketReviewForm(data={
            'title': 'Titre',
            'description': 'Texte',
            'headline': 'Critique',
            'rating': 5,
            'body': 'Commentaire'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_ticket_and_review_missing_fields(self):
        """
        TicketReviewForm → invalide si champs requis manquants / rating hors bornes.
        """
        form = TicketReviewForm(data={
            'title': '',
            'description': '',
            'headline': '',
            'rating': 10,   # > 5
            'body': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('headline', form.errors)
        self.assertIn('rating', form.errors)
        self.assertIn('body', form.errors)
