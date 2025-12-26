from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT
    Incluye información del usuario en la respuesta
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar datos del usuario al token
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información del usuario a la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener tokens JWT"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Endpoint para registrar nuevo usuario
    POST /api/auth/register/
    Body: {
        "username": "juan",
        "email": "juan@example.com",
        "password": "segura123",
        "first_name": "Juan",
        "last_name": "Pérez"
    }
    """
    
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validaciones
        if not username or not email or not password:
            return Response({
                'error': 'username, email y password son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return Response({
                'error': f'El usuario {username} ya existe'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': f'El email {email} ya está registrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el usuario
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            return Response({
                'status': 'success',
                'message': 'Usuario registrado correctamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def profile(request):
    """
    Obtener perfil del usuario autenticado
    GET /api/auth/profile/
    """
    user = request.user
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
