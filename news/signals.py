from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Article

@receiver(post_save, sender=Article)
def notify_reporter_on_publish(sender, instance, created, **kwargs):
    if not created and instance.status == "published":
        previous = Article.objects.get(pk=instance.pk)
        
        if previous.status != instance.status and instance.status == "published":
            subject = "Your article has been published!"
            message = f"Hi {instance.author.username},\n\nYour article '{instance.title}' has been published.\n\nCheck it out here: http://yourdomain.com/article/{instance.slug}/"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [instance.author.email]

            send_mail(subject, message, from_email, recipient_list)
