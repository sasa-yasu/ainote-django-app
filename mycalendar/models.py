from django.db import models
from django.contrib.auth.models import User

class GoogleOAuthToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = models.TextField()
