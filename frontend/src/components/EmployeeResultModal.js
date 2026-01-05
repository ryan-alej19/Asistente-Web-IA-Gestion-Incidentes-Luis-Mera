import React from 'react';
import './ResultModal.css';

const EmployeeResultModal = ({ incident, onClose }) => {
  if (!incident) return null;

  // Mapear severidad a español
  const severityMap = {
    'CRITICAL': { text: 'CRÍTICO', color: '#dc3545' },
    'HIGH': { text: 'ALTO', color: '#fd7e14' },
    'MEDIUM': { text: 'MEDIO', color: '#ffc107' },
    'LOW': { text: 'BAJO', color: '#28a745' }
  };

  // Mapear estado a español
  const statusMap = {
    'new': 'Nuevo',
    'in_progress': 'En revisión',
    'resolved': 'Resuelto',
    'closed': 'Cerrado'
  };

  const severity = severityMap[incident.severity] || { text: incident.severity, color: '#6c757d' };
  const status = statusMap[incident.status] || incident.status;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content employee-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <h2 className="modal-title">
          🛡️ Análisis de tu Reporte
        </h2>

        {/* RESULTADO DEL ANÁLISIS */}
        <div className="result-section">
          <h3 className="section-title">🔍 Resultado del Análisis</h3>
          
          <div className="risk-badge" style={{ backgroundColor: severity.color }}>
            <span className="risk-label">Nivel de Riesgo:</span>
            <span className="risk-value">{severity.text}</span>
            <span className="confidence">Confianza: {Math.round(incident.confidence_score)}%</span>
          </div>
        </div>

        {/* ¿POR QUÉ ES PELIGROSO? */}
        <div className="info-section">
          <h4 className="info-title">📋 ¿Por qué es peligroso?</h4>
          <p className="info-text">
            {incident.severity === 'CRITICAL' && 'Este enlace es extremadamente peligroso y podría robar tus datos personales o bancarios.'}
            {incident.severity === 'HIGH' && 'Este enlace presenta características sospechosas comúnmente usadas en ataques de phishing.'}
            {incident.severity === 'MEDIUM' && 'Este enlace tiene algunas características inusuales que requieren precaución.'}
            {incident.severity === 'LOW' && 'Este enlace no presenta señales de peligro inmediato, pero se ha registrado para seguimiento.'}
          </p>
        </div>

        {/* ¿QUÉ DEBES HACER? */}
        <div className="info-section">
          <h4 className="info-title">💡 ¿Qué debes hacer?</h4>
          <p className="info-text">
            {incident.severity === 'CRITICAL' && 'NO accedas al enlace. Elimina el correo inmediatamente. Reporta a tu supervisor.'}
            {incident.severity === 'HIGH' && 'NO ingreses información personal. Espera la confirmación del equipo de seguridad.'}
            {incident.severity === 'MEDIUM' && 'Verifica con tu supervisor antes de acceder al enlace.'}
            {incident.severity === 'LOW' && 'El incidente ha sido registrado. Puedes continuar normalmente.'}
          </p>
        </div>

        {/* ESTADO */}
        <div className="status-section">
          <h4 className="info-title">📊 Estado:</h4>
          <span className="status-badge">{status}</span>
          {incident.status === 'new' && (
            <p className="status-message">
              ⏳ Tu reporte está en revisión por el equipo de seguridad
            </p>
          )}
          {incident.status === 'in_progress' && (
            <p className="status-message">
              🔍 El equipo de seguridad está analizando tu reporte
            </p>
          )}
          {incident.status === 'resolved' && (
            <p className="status-message">
              ✅ El incidente ha sido resuelto. Gracias por reportar.
            </p>
          )}
        </div>

        {/* TU REPORTE */}
        <div className="report-summary">
          <h4>📝 Tu reporte</h4>
          <p><strong>Título:</strong> {incident.title}</p>
          {incident.url && <p><strong>URL:</strong> {incident.url}</p>}
          <p><strong>Descripción:</strong> {incident.description || 'Sin descripción'}</p>
          <p><strong>Fecha:</strong> {new Date(incident.created_at).toLocaleString('es-EC')}</p>
        </div>
      </div>
    </div>
  );
};

export default EmployeeResultModal;
