from django.db import models
from django.contrib.auth import get_user_model
# from cloudinary.models import CloudinaryField

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, default='profile_images/default.png')
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"