from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from slugify import slugify
from autoslug import AutoSlugField

class Genre(models.Model):
    title = models.TextField()  
    slug = AutoSlugField(populate_from='title', unique=True, slugify=slugify)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Title: {self.title}"
    
    def get_absolute_url(self):
        return reverse('movie_app:category_detail_view', args=(self.slug,))

class Movie(models.Model):
    movie_id = models.IntegerField()
    title = models.TextField()
    slug = AutoSlugField(populate_from='title', unique=True, slugify=slugify)
    is_active = models.BooleanField(default=True)
    overview = models.TextField()
    genre = models.ManyToManyField(Genre)
    popularity = models.FloatField()
    poster = models.URLField(null=True, blank=True) 
    video = models.URLField(null=True, blank=True)
    release_date = models.DateField()
    language = models.TextField(max_length=100, null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"Movie Title: {self.title}"
    
    def get_absolute_url(self):
        return reverse('movie_app:movie_detail_view', kwargs={'movie_slug':self.slug})
    
    class Meta:
        ordering = ("-release_date",)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment: {self.comment}"
    
    class Meta:
        ordering = ('-created_at',)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='get_username', unique=True, slugify=slugify)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='user-avatars/', default='default-avatar/default-avatar.webp')
    info = models.TextField()
    instagram = models.CharField(max_length=1024, null=True, blank=True)
    twitter = models.CharField(max_length=1024, null=True, blank=True)

    def get_username(self):
        return f"{self.user.username}"    

    def __str__(self):
        return f"{self.user.username}"
    
    def get_absolute_url(self):
        return reverse('movie_app:profile_detail_view', kwargs={'profile_slug':self.slug})
    

class Viewing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_date = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('plan_to_watch', 'Plan to Watch'),
        ('on_hold', 'On Hold'),
        ('dropped', 'Dropped')
    ]
    status = models.CharField(
        max_length=20, 
        choices=status_choices, 
        default='plan_to_watch'
    )

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-watched_date']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"