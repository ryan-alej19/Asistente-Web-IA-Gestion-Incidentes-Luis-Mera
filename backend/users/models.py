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

class LoginAttempt(models.Model):
    """
    Registro de intentos de inicio de sesión exitosos y fallidos para la auditoría de seguridad.
    """
    username = models.CharField(max_length=150, help_text="Nombre de usuario ingresado")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Dirección IP de origen")
    user_agent = models.TextField(null=True, blank=True, help_text="Navegador y sistema operativo")
    successful = models.BooleanField(default=False, help_text="¿Fue exitoso el inicio de sesión?")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora del intento")

    class Meta:
        verbose_name = 'Intento de Inicio de Sesión'
        verbose_name_plural = 'Intentos de Inicio de Sesión'
        ordering = ['-timestamp']

    def __str__(self):
        status_text = "Éxito" if self.successful else "Fallido"
        return f"{self.timestamp} - {self.username} [{self.ip_address}] - {status_text}"
