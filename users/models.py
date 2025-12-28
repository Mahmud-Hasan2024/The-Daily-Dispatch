from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = CloudinaryField('profile_image', blank=True, null=True, default='default_profile')
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"