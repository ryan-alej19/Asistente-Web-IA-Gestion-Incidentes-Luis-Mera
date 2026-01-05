import EmployeeResultModal from '../components/EmployeeResultModal';
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import IncidentAnalysisModal from '../components/IncidentAnalysisModal';
import '../styles/Dashboard.css';

function EmployeeDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [form, setForm] = useState({
    url: '',
    description: ''
  });
  const [attachedFile, setAttachedFile] = useState(null); // 🔥 NUEVO
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [myIncidents, setMyIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    fetchMyIncidents();
  }, []);

  const fetchMyIncidents = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/incidents/my-incidents/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('📋 Mis incidentes cargados:', response.data);
      setMyIncidents(response.data);
    } catch (err) {
      console.error('Error cargando incidentes:', err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 🔥 VALIDACIÓN ACTUALIZADA: al menos uno de los tres campos
    if (!form.url.trim() && !form.description.trim() && !attachedFile) {
      alert('Por favor ingresa al menos una URL, descripción o archivo adjunto');
      return;
    }

    setLoading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      
      // 🔥 USAR FormData para enviar archivos
      const formData = new FormData();
      
      // Título inteligente
      const title = form.url 
        ? `Reporte: ${form.url.substring(0, 50)}` 
        : attachedFile
        ? `Reporte: ${attachedFile.name}`
        : 'Reporte: Sin URL';
      
      formData.append('title', title);
      formData.append('description', form.description || 'Sin descripción adicional');
      formData.append('threat_type', 'phishing');
      
      if (form.url.trim()) {
        formData.append('url', form.url);
      }
      
      if (attachedFile) {
        formData.append('attached_file', attachedFile);
      }
      
      const response = await axios.post('http://localhost:8000/api/incidents/', formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          // 🔥 NO pongas Content-Type, axios lo maneja automáticamente con FormData
        }
      });
      
      console.log('✅ Incidente creado:', response.data);
      
      setSuccess(true);
      setForm({ url: '', description: '' });
      setAttachedFile(null);
      
      // Resetear input de archivo
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
      
      setTimeout(async () => {
        await fetchMyIncidents();
        setSuccess(false);
      }, 800);
      
    } catch (err) {
      console.error('❌ Error reportando incidente:', err);
      alert('Error al reportar el incidente: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = (incident) => {
    setSelectedIncident(incident);
  };

  return (
    <div className="dashboard">
      {/* HEADER */}
      <div className="dashboard-header">
        <div className="header-content">
          <div>
            <h1 className="dashboard-title">🛡️ Portal del Empleado</h1>
            <p className="welcome-message">
              ¡Hola, <strong>{user?.username}</strong>! | Rol: Empleado
            </p>
            <p className="role-description">
              Reporta enlaces sospechosos, phishing o malware para proteger a la empresa
            </p>
          </div>
          <button onClick={handleLogout} className="btn-logout">
            🚪 Cerrar Sesión
          </button>
        </div>
      </div>

      {/* FORMULARIO */}
      <div className="employee-report-section">
        <h2 className="section-title">📝 Reportar un Correo o Enlace Sospechoso</h2>
        
        {success && (
          <div className="alert alert-success">
            ✅ ¡Incidente reportado y analizado! El equipo de seguridad lo revisará.
          </div>
        )}

        <form onSubmit={handleSubmit} className="report-form">
          <div className="form-group">
            <label htmlFor="url">
              🔗 URL o Correo Sospechoso <span className="optional">(Opcional)</span>
            </label>
            <input
              id="url"
              type="text"
              name="url"
              value={form.url}
              onChange={handleChange}
              placeholder="Ej: http://suspicious-site.com o fake@email.com"
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">
              📝 Descripción <span className="optional">(Opcional)</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="¿Qué pasó? ¿Dónde lo encontraste? ¿Qué te llamó la atención?"
              rows="3"
              className="form-control"
            />
          </div>

          {/* 🔥 NUEVO: Input para archivo */}
          <div className="form-group">
            <label htmlFor="file-input">
              📎 Archivo Adjunto <span className="optional">(Opcional)</span>
            </label>
            <input
              id="file-input"
              type="file"
              accept="image/*,.pdf,.doc,.docx,.txt"
              onChange={(e) => setAttachedFile(e.target.files[0])}
              className="form-control"
            />
            {attachedFile && (
              <div style={{ 
                marginTop: '8px', 
                padding: '8px', 
                background: '#f0f9ff', 
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                📄 {attachedFile.name} ({(attachedFile.size / 1024).toFixed(2)} KB)
              </div>
            )}
            <small style={{ color: '#6b7280', fontSize: '12px', display: 'block', marginTop: '4px' }}>
              Formatos aceptados: Imágenes, PDF, Word, TXT (máx. 5MB)
            </small>
          </div>

          <button 
            type="submit" 
            className="btn-submit"
            disabled={loading || (!form.url.trim() && !form.description.trim() && !attachedFile)}
          >
            {loading ? '⏳ Analizando...' : '🚀 Reportar y Analizar'}
          </button>
        </form>
      </div>

      {/* MIS REPORTES */}
      <div className="my-incidents-section">
        <h2 className="section-title">📋 Mis Reportes</h2>
        {myIncidents.length === 0 ? (
          <div className="no-incidents">
            <p>📭 No has reportado ningún incidente aún.</p>
            <p>Usa el formulario de arriba para reportar URLs o correos sospechosos.</p>
          </div>
        ) : (
          <div className="incidents-table">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>URL/Email</th>
                  <th>Severidad</th>
                  <th>Estado</th>
                  <th>Detalles</th>
                </tr>
              </thead>
              <tbody>
                {myIncidents.map(incident => (
                  <tr key={incident.id}>
                    <td>{new Date(incident.created_at).toLocaleDateString('es-ES')}</td>
                    <td className="url-cell">
                      {incident.url ? (
                        <span title={incident.url}>{incident.url}</span>
                      ) : incident.attached_file ? (
                        <span className="no-url">📎 {incident.title}</span>
                      ) : (
                        <span className="no-url">{incident.title}</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge badge-${incident.severity}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className={`status status-${incident.status.replace('_', '-')}`}>
                        {incident.status === 'new' ? 'En revisión' : 
                         incident.status === 'in_progress' ? 'En progreso' :
                         incident.status === 'resolved' ? 'Resuelto' : 'Crítico'}
                      </span>
                    </td>
                    <td className="details-cell">
                      <button 
                        className="btn-analyze"
                        onClick={() => handleAnalyze(incident)}
                      >
                        🔍 Analizar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* MODAL DE ANÁLISIS */}
      {selectedIncident && (
        <IncidentAnalysisModal 
          incident={selectedIncident}
          onClose={() => setSelectedIncident(null)}
          userRole="employee"
        />
      )}
    </div>
  );
}

export default EmployeeDashboard;
