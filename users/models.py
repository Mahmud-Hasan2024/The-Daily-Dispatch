from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(null=True, blank=True)
    profile_image = CloudinaryField('image', blank=True, null=True, default='default_images/vt7vpmt0jpiapfyws2bh')
    
    def __str__(self):
        return f"{self.user.username} Profile"