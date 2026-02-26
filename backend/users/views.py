from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, update_last_login
from django.shortcuts import get_object_or_404
from .models import UserProfile, LoginAttempt
import logging

auth_log = logging.getLogger('auth_logger')

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        username = request.data.get('username', 'N/A')

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        
        if not serializer.is_valid():
            LoginAttempt.objects.create(
                username=username,
                ip_address=client_ip,
                user_agent=user_agent,
                successful=False
            )
            auth_log.warning(f"LOGIN FALLIDO - Usuario: {username} | IP: {client_ip} | Motivo: Credenciales incorrectas")
            return Response({'non_field_errors': ['Credenciales invalidas']}, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Update last_login
        update_last_login(None, user)
        
        role = 'employee'
        if hasattr(user, 'profile'):
            role = user.profile.role
        
        LoginAttempt.objects.create(
            username=user.username,
            ip_address=client_ip,
            user_agent=user_agent,
            successful=True
        )
        auth_log.info(f"LOGIN EXITOSO - Usuario: {username} | Rol: {role} | IP: {client_ip}")
            
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'role': role
        })

from .serializers import UserSerializer, LoginAttemptSerializer
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class IsAdminUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol 'admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                    hasattr(request.user, 'profile') and 
                    request.user.profile.role == 'admin')

class LoginAttemptListView(generics.ListAPIView):
    """
    Lista todos los intentos de inicio de sesión.
    Solo accesible para administradores.
    """
    queryset = LoginAttempt.objects.all()
    serializer_class = LoginAttemptSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        # Prevent deactivating self
        if user == request.user:
            return Response({'error': 'No puedes desactivar tu propia cuenta'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.is_active = not user.is_active
        user.save()
        
        status_msg = "activado" if user.is_active else "desactivado"
        return Response({'message': f'Usuario {user.username} {status_msg} correctamente', 'is_active': user.is_active})

class ChangeUserRoleView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_role = request.data.get('role')
        
        if not new_role in ['admin', 'analyst', 'employee']:
             return Response({'error': 'Rol inválido'}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent changing self role (optional but safe)
        if user == request.user:
             return Response({'error': 'No puedes cambiar tu propio rol'}, status=status.HTTP_400_BAD_REQUEST)

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = new_role
        profile.save()
        
        return Response({'message': f'Rol de {user.username} actualizado a {new_role}', 'role': new_role})
