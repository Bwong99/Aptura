from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    PHOTO_GENRES = [
        ('landscape', 'Landscape'),
        ('portrait', 'Portrait'),
        ('city', 'City'),
        ('street', 'Street'),
        ('nature', 'Nature'),
        ('pet', 'Pet'),
        ('architecture', 'Architecture'),
        ('drone', 'Drone'),
        ('wedding', 'Wedding'),
        ('fashion', 'Fashion'),
        ('sports', 'Sports'),
        ('documentary', 'Documentary'),
        ('product', 'Product'),
        ('food', 'Food'),
        ('abstract', 'Abstract'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_photo = CloudinaryField('image', blank=True, null=True)
    favorite_post = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='favorited_by')
    photo_genres = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_genre_display_names(self):
        genre_dict = dict(self.PHOTO_GENRES)
        return [genre_dict.get(genre, genre) for genre in self.photo_genres]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    photo = CloudinaryField('image')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"

class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate saves
    
    def __str__(self):
        return f"{self.user.username} saved {self.post.title}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('save', 'Save'),
        ('post', 'New Post'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.message}"

class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    posts = models.ManyToManyField(Post, blank=True, related_name='albums')
    cover_photo = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='album_covers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
