from rest_framework import serializers
from .models import Incident

class IncidentSerializer(serializers.ModelSerializer):
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)

    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'reported_by', 'virustotal_result', 'phishtank_result', 'metadefender_result')
