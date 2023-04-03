from email.policy import default
from django.db import models
from django.contrib.auth import get_user_model
import uuid
# Create your models here.

User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    def __str__(self):
        return self.user.username


class auto(models.Model):
    id_auto = models.CharField(max_length=32, primary_key=True, default=uuid.uuid4, editable=False)
    marka = models.TextField(max_length=100)
    model = models.TextField(max_length=100)
    cena = models.TextField(max_length=100, default=0)
    litry = models.TextField(max_length=100, default=0)
    lcena = models.TextField(max_length=100, default=0)
    image = models.FileField(upload_to='images', blank=True)
    connection = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    def hex_uuid():
        return uuid.uuid4().hex

class history(models.Model):
    id_history = models.CharField(max_length=32, primary_key=True, default=uuid.uuid4, editable=False)
    cena_h = models.TextField(max_length=100, default=0)
    litry_h = models.TextField(max_length=100, default=0)
    lcena_h = models.TextField(max_length=100, default=0)
    data = models.DateTimeField(default=0)
    connection_h = models.ForeignKey(auto, on_delete=models.CASCADE)

    def hex_uuid():
        return uuid.uuid4().hex