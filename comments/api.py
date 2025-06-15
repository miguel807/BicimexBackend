from logging import Logger
from rest_framework.decorators import action
from .models import Comment, Feedback, UserProfile
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import F
from rest_framework import status
from comments.serializer import CommentSerializer, FeedbackSerializer,CreateCommentSerializer
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return CreateCommentSerializer if self.action == 'create' else CommentSerializer

    def create(self, request, *args, **kwargs):
       
        print("\n=== Datos de request ===")
        print("Raw data:", request.data)
    
       
        modified_data = request.data.copy()
    
      
        replying_to_username = modified_data.get('replying_to')
        if replying_to_username:
            try:
               
                user_to_reply = UserProfile.objects.get(username=replying_to_username)
                modified_data['replying_to'] = user_to_reply.id  
                print(f"Usuario a responder encontrado - ID: {user_to_reply.id}")
            except UserProfile.DoesNotExist:
                return Response(
                    {"error": f"Usuario '{replying_to_username}' no encontrado"},
                    status=status.HTTP_400_BAD_REQUEST
                )
    
      
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
    
      
        try:
            default_user = UserProfile.objects.get(id=1)
            print(f"Usuario predeterminado asignado - ID: {default_user.id}")
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Usuario predeterminado no configurado"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
    
      
        try:
            comment = Comment.objects.create(
                user=default_user,
                **serializer.validated_data
             )
            print(f"Comentario creado exitosamente - ID: {comment.id}")
        
          
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"Error al crear comentario: {str(e)}")
            return Response(
                {"error": "Error interno al crear el comentario"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    permission_classes = [permissions.AllowAny] 
    serializer_class = FeedbackSerializer

   
    def get_queryset(self):
        queryset = super().get_queryset()
    
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        try:
            feedback = self.get_object()
            feedback.upvotes = F('upvotes') + 1  
            feedback.save()
            feedback.refresh_from_db()  
            
            return Response({
                'status': 'success',
                'upvotes': feedback.upvotes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # Opcional: Personalizar la creación de feedback
    def perform_create(self, serializer):
        # Obtener el UserProfile con ID 1 (o el que corresponda)
        try:
            user_profile = UserProfile.objects.get(id=1)
            serializer.save(author=user_profile)
        except Exception as e:
            Logger.error(f"Error al asignar UserProfile: {str(e)}")
     
    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save()     