from django.db import models
from users.models import User

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)