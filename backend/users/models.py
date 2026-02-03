from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Perfil extendido de usuario con rol especifico.
    Empleado: reporta incidentes
    Analista: gestiona y analiza incidentes
    Admin: administra sistema y usuarios
    """
    
    ROLE_CHOICES = [
        ('employee', 'Empleado'),
        ('analyst', 'Analista'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# Crear perfil automaticamente al crear usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
