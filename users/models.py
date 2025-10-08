from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, default='profile_images/default.png')
    
    def __str__(self):
        return f"{self.user.username} Profile"
