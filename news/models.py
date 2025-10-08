from django.db import models
from users.forms import User
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("published", "Published"),
    )
        
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,  related_name="articles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
