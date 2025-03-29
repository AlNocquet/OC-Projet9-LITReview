from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Ticket(models.Model):

    """
    Model representing a review request (ticket).

    Fields:
    - title: title of the book or article.
    - description: optional description of the request.
    - user: user who created the ticket.
    - image: optional associated image.
    - time_created: timestamp of ticket creation.
    """

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image =  models.ImageField (null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)



class Review(models.Model):

    """
    Model representing a review of a book or article.

    Fields:
    - rating: rating score (from 0 to 5 inclusive).
    - headline: title of the review.
    - body: review content (optional).
    - user: user who wrote the review.
    - ticket: ticket associated with this review.
    - time_created: timestamp of review creation.
    """

    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)]) 
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE) 
        # Enregistre l'ID d'un Ticket dans chaque Review
        # Permet d'accéder directement à l'objet Ticket via review.ticket
        # Dde récupérer toutes les reviews associées via ticket.review_set
    time_created = models.DateTimeField(auto_now_add=True)



class UserFollows(models.Model):

    """
    Model representing a follow relationship between users.

    Fields:
    - user: the follower (who follows others).
    - followed_user: the user being followed.

    Notes:
    - user.following.all() returns all follow relationships where the user is the follower.
    - user.followed_by.all() returns all follow relationships where the user is being followed.

    Constraints:
    - Each user can follow another user only once (unique_together).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_by')
        # user.following.all() renverra tous les enregistrements de suivi où il est le follower ;
        # user.followed_by.all() donnera tous les enregistrements où il est suivi.

    class Meta :
        unique_together = ('user', 'followed_user') 
            # Contrainte : Ne peut suivre un autre utilisateur qu'une seule fois ;
