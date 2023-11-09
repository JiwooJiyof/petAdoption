from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from accounts.models import PetSeeker, Shelter
from applications.models import Application


# Create your models here.
class Comment(models.Model):
    body = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    # TODO switch to our custom user
    author = models.ForeignKey(PetSeeker, on_delete=models.CASCADE)


class ShelterComment(Comment):
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    # reply = models.ForeignKey(Reply, null=True, on_delete=models.CASCADE)


class ApplicationComment(Comment):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)