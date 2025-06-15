from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Feedback, Comment, UserProfile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
   
    id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'name', 'image']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    replying_to = UserProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 
            'content', 
            'created_at', 
            'user', 
            'replying_to',
            'replies',
            'feedback',
            'parent_comment'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'replying_to', 'replies']
    
    def get_replies(self, obj):
        replies = obj.replies.all().order_by('created_at')
        return CommentSerializer(replies, many=True).data
    

class CreateCommentSerializer(serializers.ModelSerializer):
    replying_to_username = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Username del usuario al que se responde"
    )

    class Meta:
        model = Comment
        fields = ['content', 'feedback', 'parent_comment', 'replying_to_username']
        extra_kwargs = {
            'parent_comment': {'required': False},
            'feedback': {'required': True}
        }

class FeedbackSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    upvotes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Feedback
        fields = [
            'id',
            'title',
            'description',
            'category',
            'status',
            'upvotes',
            'upvotes_count',
            'created_at',
            'updated_at',
            'author',
            'comments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_upvotes_count(self, obj):
        """Método para contar upvotes"""
        return obj.upvotes
    
class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'feedback', 'parent_comment', 'replying_to']
    
    def validate(self, data):
        """Validación personalizada para comentarios"""
        if data.get('parent_comment') and not data.get('replying_to'):
            raise serializers.ValidationError(
                "Cuando se responde a un comentario, se debe especificar replying_to"
            )
        return data

class CreateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['title', 'description', 'category', 'status']