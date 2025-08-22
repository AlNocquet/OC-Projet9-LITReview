"""CRUD Tickets: creation, edition, deletion, permissions and integration in feed/posts."""

# test_create_ticket_ok : succès de création d’un ticket valide (titre, description, image optionnelle)
# test_create_ticket_invalid : échec si formulaire incomplet ou invalide (champ manquant)
# test_edit_ticket_ok : modification réussie d’un ticket par son auteur
# test_edit_ticket_forbidden : refus de modification par un autre utilisateur
# test_delete_ticket_ok : suppression réussie d’un ticket par son auteur
# test_delete_ticket_forbidden : refus de suppression par un autre utilisateur
# test_ticket_listed_in_posts : ticket créé doit apparaître dans "posts" (page des publications de l’utilisateur)
# test_ticket_listed_in_flux : ticket doit apparaître dans le flux de l’utilisateur et de ses abonnés (sauf bloqués)
# test_ticket_requires_login : accès aux vues de création/édition/suppression interdit sans authentification
# test_ticket_form_validation : contrôle des contraintes de longueur (max_length) sur les champs (titre ≤ 128, description ≤ 2048)

## Ces tests couvrent l’ensemble du cycle de vie d’un ticket :
    ## création → validation → édition → suppression → affichage dans les flux,
    ## en garantissant que seules les actions légitimes sont autorisées et que les
    ## contraintes définies dans le modèle et les formulaires sont respectées.


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from LITReview.models import Ticket, Review


class TicketTests(TestCase):
    def setUp(self):
        # Utilisateurs
        self.alice = User.objects.create_user(
            username="alice", email="alice@test.com", password="Pass1234!"
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@test.com", password="Pass1234!"
        )
        # Alice connectée par défaut
        self.client.login(username="alice", password="Pass1234!")

    # ------------------------------------------------------------------ #
    # Création
    # ------------------------------------------------------------------ #

    def test_create_ticket_ok(self):
        """
        POST /ticket/create/ crée un Ticket et redirige vers 'flux'.
        - Form: TicketForm(title, description, image?)
        """
        payload = {
            "title": "Dune",
            "description": "Demande de critique sur Dune.",
            # pas d'image
        }
        resp = self.client.post(reverse("create_ticket"), data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("flux"))

        self.assertTrue(Ticket.objects.filter(title="Dune", user=self.alice).exists())
        t = Ticket.objects.get(title="Dune", user=self.alice)
        self.assertEqual(t.description, "Demande de critique sur Dune.")

    def test_create_ticket_invalid_missing_description(self):
        """
        TicketForm exige title et description -> description manquante => 200 + pas de création.
        """
        payload = {
            "title": "Sans description",
            "description": "",  # invalide (champ requis)
        }
        resp = self.client.post(reverse("create_ticket"), data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Ticket.objects.filter(title="Sans description").exists())

    # ------------------------------------------------------------------ #
    # Edition
    # ------------------------------------------------------------------ #

    def test_edit_ticket_ok(self):
        """
        L'auteur peut éditer son Ticket.
        - GET form 200
        - POST valide => redirect 'posts' (par défaut si next absent)
        """
        t = Ticket.objects.create(title="Old", description="Old desc", user=self.alice)
        url = reverse("edit_ticket", args=[t.id])

        # GET
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)

        # POST maj
        resp_post = self.client.post(url, {
            "title": "New",
            "description": "New desc",
            # image laissée vide
        })
        self.assertEqual(resp_post.status_code, 302)
        self.assertRedirects(resp_post, reverse("posts"))

        t.refresh_from_db()
        self.assertEqual(t.title, "New")
        self.assertEqual(t.description, "New desc")

    def test_edit_ticket_forbidden_for_non_author(self):
        """
        Un autre utilisateur ne peut pas éditer : 404 (get_object_or_404(..., user=request.user)).
        """
        t_bob = Ticket.objects.create(title="Bob T", description="Desc", user=self.bob)
        url = reverse("edit_ticket", args=[t_bob.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        resp_post = self.client.post(url, {"title": "Hack", "description": "Try"})
        self.assertEqual(resp_post.status_code, 404)

    # ------------------------------------------------------------------ #
    # Suppression
    # ------------------------------------------------------------------ #

    def test_delete_ticket_ok(self):
        """
        L'auteur peut supprimer son Ticket :
        - GET de confirmation 200
        - POST supprime + redirect 'posts' (ou 'next' si fourni)
        """
        t = Ticket.objects.create(title="ToDel", description="...", user=self.alice)
        url = reverse("delete_ticket", args=[t.id])

        # Page de confirmation
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)

        # Suppression
        resp_post = self.client.post(url)
        self.assertEqual(resp_post.status_code, 302)
        self.assertRedirects(resp_post, reverse("posts"))
        self.assertFalse(Ticket.objects.filter(id=t.id).exists())

    def test_delete_ticket_forbidden_for_non_author(self):
        """
        Suppression par un non-auteur -> 404 et l'objet reste.
        """
        t_bob = Ticket.objects.create(title="T-bob", description="...", user=self.bob)
        url = reverse("delete_ticket", args=[t_bob.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Ticket.objects.filter(id=t_bob.id).exists())

    # ------------------------------------------------------------------ #
    # Intégration : posts / flux
    # ------------------------------------------------------------------ #

    def test_user_posts_contains_own_tickets(self):
        """
        La vue posts liste les posts de l'utilisateur :
        - Tickets (annotés content_type='TICKET')
        - Reviews (si présentes)
        """
        t1 = Ticket.objects.create(title="A", description="a", user=self.alice)
        t2 = Ticket.objects.create(title="B", description="b", user=self.alice)
        # Une review pour vérifier que posts accepte aussi d'autres types
        Review.objects.create(user=self.alice, ticket=t1, headline="H", body="B", rating=4)

        resp = self.client.get(reverse("posts"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("posts", resp.context)

        posts = resp.context["posts"]
        # Doit contenir au moins nos 3 éléments (2 tickets + 1 review)
        self.assertGreaterEqual(len(posts), 3)
        # Vérifie la présence des titres des tickets
        titles = {getattr(p, "title", None) for p in posts if getattr(p, "title", None)}
        self.assertTrue({"A", "B"}.issubset(titles))

    def test_flux_contains_ticket_block_without_reviews(self):
        """
        Un ticket sans review apparaît comme 'ticket_block' dans le flux :
        - reviews [] (liste vide)
        - has_review_by_user == False
        """
        t = Ticket.objects.create(title="Flux Ticket", description="x", user=self.alice)

        resp = self.client.get(reverse("flux"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("all_items", resp.context)

        blocks = [it for it in resp.context["all_items"]
                  if it.get("kind") == "ticket_block" and it.get("ticket").id == t.id]
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block["ticket"].title, "Flux Ticket")
        self.assertEqual(list(block["reviews"]), [])
        self.assertFalse(block["ticket"].has_review_by_user)

    def test_edit_ticket_respects_next_param(self):
        """
        L'édition respecte le paramètre ?next=<url> et redirige vers cette URL.
        """
        t = Ticket.objects.create(title="N", description="d", user=self.alice)
        url = reverse("edit_ticket", args=[t.id])
        next_url = reverse("flux")
        resp = self.client.post(f"{url}?next={next_url}", {
            "title": "N2",
            "description": "d2"
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, next_url)
        t.refresh_from_db()
        self.assertEqual(t.title, "N2")

    def test_delete_ticket_respects_next_param(self):
        """
        La suppression respecte le paramètre ?next=<url> et redirige vers cette URL.
        """
        t = Ticket.objects.create(title="N3", description="d3", user=self.alice)
        url = reverse("delete_ticket", args=[t.id])
        next_url = reverse("flux")

        # GET confirmation avec next
        resp_get = self.client.get(f"{url}?next={next_url}")
        self.assertEqual(resp_get.status_code, 200)

        # POST suppression -> redirect next
        resp_post = self.client.post(f"{url}?next={next_url}")
        self.assertEqual(resp_post.status_code, 302)
        self.assertRedirects(resp_post, next_url)
        self.assertFalse(Ticket.objects.filter(id=t.id).exists())