import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import IncidentAnalysisModal from '../components/IncidentAnalysisModal';
import '../styles/Dashboard.css';

function AnalystDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    fetchIncidents();
    fetchStats();
  }, []);

  const fetchIncidents = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/incidents/my-incidents/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('📋 Incidentes del Analyst:', response.data);
      setIncidents(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error cargando incidentes:', err);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/dashboard/stats/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (err) {
      console.error('Error cargando stats:', err);
    }
  };

  const handleAnalyze = (incident) => {
    setSelectedIncident(incident);
  };

  const handleCloseModal = () => {
    setSelectedIncident(null);
  };

  const handleUpdate = () => {
    fetchIncidents();
    fetchStats();
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) return <div className="dashboard-loading">Cargando...</div>;

  const analysisData = [
    { status: 'Nuevos', count: stats?.open || 0 },
    { status: 'En Progreso', count: stats?.in_progress || 0 },
    { status: 'Resueltos', count: stats?.closed || 0 }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div>
            <h1 className="dashboard-title">🔍 Panel de Analista de Seguridad</h1>
            <p className="welcome-message">
              ¡Hola, <strong>{user?.username}</strong>! | Rol: Analista SOC
            </p>
            <p className="role-description">
              Analiza, revisa y gestiona incidentes de seguridad reportados
            </p>
          </div>
          <button onClick={handleLogout} className="btn-logout">
            🚪 Cerrar Sesión
          </button>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card stat-blue">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <p className="stat-label">Total Asignados</p>
            <p className="stat-value">{incidents.length}</p>
          </div>
        </div>

        <div className="stat-card stat-orange">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <p className="stat-label">Nuevos (Sin Revisar)</p>
            <p className="stat-value">{stats?.open || 0}</p>
          </div>
        </div>

        <div className="stat-card stat-green">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <p className="stat-label">Resueltos</p>
            <p className="stat-value">{stats?.closed || 0}</p>
          </div>
        </div>
      </div>

      <div className="analyst-section">
        <h2 className="section-title">🎯 Incidentes Asignados</h2>
        
        {incidents.length === 0 ? (
          <div className="no-incidents">
            <p>No hay incidentes asignados en este momento.</p>
          </div>
        ) : (
          <div className="incidents-table">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Título</th>
                  <th>Severidad</th>
                  <th>Estado</th>
                  <th>Confianza IA</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {incidents.map(incident => (
                  <tr key={incident.id}>
                    <td>{new Date(incident.created_at).toLocaleDateString()}</td>
                    <td className="title-cell">{incident.title}</td>
                    <td>
                      <span className={`badge badge-${incident.severity}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className={`status status-${incident.status.replace('_', '-')}`}>
                        {incident.status === 'new' ? 'Nuevo' : 
                         incident.status === 'in_progress' ? 'En progreso' :
                         incident.status === 'resolved' ? 'Resuelto' : 'Crítico'}
                      </span>
                    </td>
                    <td className="confidence-cell">
                      {Math.round(incident.confidence * 100)}%
                    </td>
                    <td className="action-cell">
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

      <div className="chart-container analyst-chart">
        <h3>📊 Distribución de Incidentes</h3>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={analysisData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3b82f6" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="quick-actions">
        <h2 className="section-title">⚡ Acciones Rápidas</h2>
        <div className="action-buttons">
          <button 
            className="action-btn btn-primary"
            onClick={() => alert('Función en desarrollo')}
          >
            📝 Generar Reporte Semanal
          </button>
          <button 
            className="action-btn btn-secondary"
            onClick={() => { fetchIncidents(); fetchStats(); }}
          >
            🔄 Actualizar Lista
          </button>
          <button 
            className="action-btn btn-tertiary"
            onClick={() => alert('Función en desarrollo')}
          >
            📧 Notificar Admin
          </button>
        </div>
      </div>

      {selectedIncident && (
        <IncidentAnalysisModal 
          incident={selectedIncident}
          onClose={handleCloseModal}
          onUpdate={handleUpdate}
        />
      )}
    </div>
  );
}

export default AnalystDashboard;
