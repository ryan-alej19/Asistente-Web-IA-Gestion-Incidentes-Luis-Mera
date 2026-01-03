import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './IncidentAnalysisModal.css';

function IncidentAnalysisModal({ incident, onClose, onUpdate }) {
  const [newStatus, setNewStatus] = useState(incident?.status || 'new');
  const [notes, setNotes] = useState('');
  const [updating, setUpdating] = useState(false);

  // Actualizar el estado interno si el incidente cambia
  useEffect(() => {
    if (incident) {
      setNewStatus(incident.status);
      setNotes(incident.analyst_notes || '');
    }
  }, [incident]);

  if (!incident) return null;

  const handleUpdateStatus = async () => {
    if (newStatus === incident.status && notes === incident.analyst_notes) {
      alert('No hay cambios para actualizar');
      return;
    }

    setUpdating(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.patch(
        `http://localhost:8000/api/incidents/${incident.id}/`,
        { 
          status: newStatus,
          analyst_notes: notes 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert('✅ Estado actualizado correctamente');
      onUpdate();
      onClose();
    } catch (err) {
      console.error('Error actualizando:', err);
      alert('Error al actualizar: ' + (err.response?.data?.error || err.message));
    } finally {
      setUpdating(false);
    }
  };

  const handleGeneratePDF = () => {
    alert('🔧 Generación de PDF en desarrollo');
  };

  const getSeverityColor = (severity) => {
    const colors = {
      'critical': '#dc2626',
      'high': '#ea580c',
      'medium': '#ca8a04',
      'low': '#16a34a'
    };
    return colors[severity?.toLowerCase()] || '#6b7280';
  };

  const getStatusLabel = (status) => {
    const labels = {
      'new': 'Nuevo',
      'in_progress': 'En Progreso',
      'resolved': 'Resuelto',
      'critical': 'Crítico'
    };
    return labels[status] || status;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔍 Análisis de Incidente #{incident.id}</h2>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <section className="info-section">
            <h3>📋 Información del Reporte</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Título:</span>
                <span className="info-value">{incident.title}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Fecha:</span>
                <span className="info-value">
                  {incident.created_at ? new Date(incident.created_at).toLocaleString('es-ES') : 'N/A'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Reportado por:</span>
                <span className="info-value">Empleado</span>
              </div>
            </div>

            <div className="description-box">
              <span className="info-label">Descripción:</span>
              <p>{incident.description || 'Sin descripción'}</p>
            </div>

            {incident.url && (
              <div className="url-box">
                <span className="info-label">🔗 URL Reportada:</span>
                <code>{incident.url}</code> {/* CORREGIDO: etiqueta code añadida */}
              </div>
            )}
          </section>

          <section className="analysis-section">
            <h3>🤖 Análisis Automático (IA)</h3>
            <div className="analysis-grid">
              <div className="analysis-card">
                <span className="analysis-label">Severidad</span>
                <span 
                  className="analysis-value"
                  style={{ color: getSeverityColor(incident.severity) }}
                >
                  {incident.severity?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              <div className="analysis-card">
                <span className="analysis-label">Confianza IA</span>
                <span className="analysis-value confidence">
                  {incident.confidence ? Math.round(incident.confidence * 100) : 0}%
                </span>
              </div>
              <div className="analysis-card">
                <span className="analysis-label">Tipo de Amenaza</span>
                <span className="analysis-value">
                  {incident.threat_type || 'No identificado'}
                </span>
              </div>
            </div>

            <div className="recommendation-box">
              <h4>💡 Recomendación:</h4>
              {incident.severity === 'critical' && (
                <p className="rec-critical">❌ <strong>NO HACER CLIC</strong> - Amenaza crítica detectada.</p>
              )}
              {incident.severity === 'high' && (
                <p className="rec-high">⚠️ <strong>PRECAUCIÓN</strong> - Amenaza alta detectada.</p>
              )}
              {/* Otros estados de severidad... */}
            </div>
          </section>

          <section className="status-section">
            <h3>⚙️ Gestión de Estado</h3>
            <div className="status-controls">
              <div className="form-group">
                <label>Estado Actual:</label>
                <span className={`status status-${incident.status}`}>
                  {getStatusLabel(incident.status)}
                </span>
              </div>

              <div className="form-group">
                <label htmlFor="newStatus">Cambiar a:</label>
                <select 
                  id="newStatus"
                  value={newStatus} 
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="form-control"
                >
                  <option value="new">Nuevo</option>
                  <option value="in_progress">En Progreso</option>
                  <option value="resolved">✅ Resuelto (No era amenaza)</option>
                  <option value="critical">⚠️ Marcar como Crítico</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="notes">Notas del Analista:</label>
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Ej: Verificado con VirusTotal..."
                  rows="3"
                  className="form-control"
                />
              </div>

              <button 
                onClick={handleUpdateStatus}
                className="btn-update"
                disabled={updating}
              >
                {updating ? '⏳ Actualizando...' : '✅ Actualizar Estado'}
              </button>
            </div>
          </section>
        </div>

        <div className="modal-footer">
          <button onClick={handleGeneratePDF} className="btn-pdf">📄 Generar Reporte PDF</button>
          <button onClick={onClose} className="btn-cancel">Cerrar</button>
        </div>
      </div>
    </div>
  );
}

export default IncidentAnalysisModal;