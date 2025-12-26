from rest_framework import serializers
from .models import Incident
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer para datos del usuario"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class IncidentSerializer(serializers.ModelSerializer):
    """
    Serializer para Incidentes
    Transforma el modelo Incident a JSON y valida datos entrantes
    """
    
    # Campos anidados para lectura
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Campos calculados
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    confidence_percentage = serializers.SerializerMethodField()
    is_critical = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id',
            'title',
            'description',
            'severity',
            'severity_display',
            'status',
            'status_display',
            'confidence',
            'confidence_percentage',
            'threat_type',
            'detected_at',
            'created_at',
            'updated_at',
            'resolved_at',
            'assigned_to',
            'assigned_to_id',
            'notes',
            'log_source',
            'ip_source',
            'ip_destination',
            'is_critical',
        ]
        read_only_fields = [
            'id',
            'detected_at',
            'created_at',
            'updated_at',
            'severity_display',
            'status_display',
            'is_critical',
        ]
    
    def get_confidence_percentage(self, obj):
        """Retorna confianza como porcentaje"""
        return int(obj.confidence * 100)
    
    def get_is_critical(self, obj):
        """Verifica si el incidente es crítico"""
        return obj.is_critical()
    
    def validate_confidence(self, value):
        """Valida que confidence esté entre 0 y 1"""
        if not (0 <= value <= 1):
            raise serializers.ValidationError(
                "Confidence debe estar entre 0 y 1 (0% - 100%)"
            )
        return value
    
    def validate_severity(self, value):
        """Valida que severity sea un valor válido"""
        valid_choices = ['low', 'medium', 'high', 'critical']
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Severity debe ser uno de: {', '.join(valid_choices)}"
            )
        return value
    
    def validate_status(self, value):
        """Valida que status sea un valor válido"""
        valid_choices = ['new', 'under_review', 'resolved', 'false_positive', 'in_progress']
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Status debe ser uno de: {', '.join(valid_choices)}"
            )
        return value
    
    def validate(self, data):
        """Validación a nivel de objeto"""
        # No permitir IP inválidas (si están presentes)
        if 'ip_source' in data and data['ip_source']:
            # La validación de IP ya ocurre en el modelo
            pass
        
        return data
    
    def create(self, validated_data):
        """Crea un nuevo incidente"""
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        incident = Incident.objects.create(**validated_data)
        
        # Asignar usuario si se proporcionó
        if assigned_to_id:
            try:
                user = User.objects.get(id=assigned_to_id)
                incident.assigned_to = user
                incident.save()
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'assigned_to_id': f'Usuario con ID {assigned_to_id} no existe'
                })
        
        return incident
    
    def update(self, instance, validated_data):
        """Actualiza un incidente existente"""
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Asignar usuario si se proporcionó
        if assigned_to_id is not None:
            if assigned_to_id:
                try:
                    user = User.objects.get(id=assigned_to_id)
                    instance.assigned_to = user
                except User.DoesNotExist:
                    raise serializers.ValidationError({
                        'assigned_to_id': f'Usuario con ID {assigned_to_id} no existe'
                    })
            else:
                instance.assigned_to = None
        
        instance.save()
        return instance


class IncidentListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar incidentes
    Usa menos campos para mejores performances en listados
    """
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    confidence_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id',
            'title',
            'severity',
            'severity_display',
            'status',
            'status_display',
            'confidence_percentage',
            'detected_at',
            'threat_type',
        ]
    
    def get_confidence_percentage(self, obj):
        return int(obj.confidence * 100)


class IncidentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear incidentes (validación estricta)"""
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Incident
        fields = [
            'title',
            'description',
            'severity',
            'status',
            'confidence',
            'threat_type',
            'assigned_to_id',
            'notes',
            'log_source',
            'ip_source',
            'ip_destination',
        ]
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "El título debe tener al menos 5 caracteres"
            )
        return value
    
    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 10 caracteres"
            )
        return value
