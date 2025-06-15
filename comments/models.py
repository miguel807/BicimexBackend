from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Feedback(models.Model):
    STATUS_CHOICES = [
        ('suggestion', 'Suggestion'),
        ('planned', 'Planned'),
        ('in-progress', 'In Progress'),
        ('live', 'Live'),
    ]
    
    CATEGORY_CHOICES = [
        ('feature', 'Feature'),
        ('enhancement', 'Enhancement'),
        ('bug', 'Bug'),
        ('ui', 'UI'),
        ('ux', 'UX'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='suggestion')
    upvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        'UserProfile',  
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-upvotes']

class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(  
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    replying_to = models.ForeignKey(  # Cambia User por UserProfile
        'UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies_received'
    )
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['created_at']

class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=250, unique=True)
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username