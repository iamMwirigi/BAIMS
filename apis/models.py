from django.db import models

# Create your models here.

class User(models.Model):
    """User model representing field agents/users"""
    name = models.CharField(max_length=64)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    region = models.CharField(max_length=64)
    active_status = models.IntegerField(default=1)
    place_holder = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.name} ({self.username})"
    
    @property
    def is_active(self):
        """Check if user is active"""
        return self.active_status == 1
