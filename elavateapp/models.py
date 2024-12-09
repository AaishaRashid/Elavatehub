from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(
        max_length=20,
        choices=[
            ('entrepreneur', 'Entrepreneur'),
            ('mentor', 'Mentor'),
            ('artist', 'Artist')
        ],
        default='entrepreneur',
    )
    # Other fields remain unchanged

    bio = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    @property
    def is_complete(self):
        return bool(self.bio and self.tags and self.profile_picture)


class Idea(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ideas")
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='idea_images/', blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_ideas", blank=True)

    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.idea.title}"


class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Successful', 'Successful'),
            ('Failed', 'Failed'),
        ],
        default='Pending',
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation by {self.user.username} - {self.amount} - {self.status}"
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
