import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ReportingPage from './pages/ReportingPage';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
<<<<<<< HEAD
=======
  const API_BASE = 'http://127.0.0.1:8000/api';
  const [currentView, setCurrentView] = useState('login');
  const [incidents, setIncidents] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ===== CARGA DE DATOS =====
  
  // Cargar incidentes REALES desde BD
  const loadIncidents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/incidents/`);
      console.log('Incidentes cargados de BD:', response.data);
      setIncidents(response.data);
      setError(null);
    } catch (error) {
      console.error('Error cargando incidentes:', error);
      setError('Error al cargar incidentes');
      setIncidents([]);
    }
  };

  // Cargar estadísticas REALES desde BD
  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/incidents/stats/`);
      console.log('Estadísticas cargadas de BD:', response.data);
      setDashboardStats(response.data);
      setError(null);
    } catch (error) {
      console.error('Error cargando dashboard:', error);
      setError('Error al cargar estadísticas');
    }
  };

  // Función login
  const handleLogin = (email, role) => {
    if (role === 'admin') {
      setCurrentView('admin');
      loadDashboardData();
      loadIncidents();
    } else {
      setCurrentView('employee');
      loadIncidents();
    }
  };

  // ===== CREAR INCIDENTE =====
  const createIncident = async (description, threatType) => {
    setLoading(true);
    try {
      // PASO 1: Crear incidente en BD
      const createResponse = await axios.post(`${API_BASE}/incidents/`, {
        description: description,
        threat_type: threatType || 'OTRO',
        criticality: 'MEDIO',
        resolved: false
      });
      
      const newIncident = createResponse.data;
      console.log('Incidente creado:', newIncident);
      
      // PASO 2: Hacer análisis IA en el incidente creado
      const analysisResponse = await axios.post(
        `${API_BASE}/incidents/${newIncident.id}/analyze/`,
        {}
      );
      
      console.log('Análisis completado:', analysisResponse.data);
      
      // PASO 3: Recargar lista de incidentes para ver el nuevo
      await loadIncidents();
      
      setError(null);
      setLoading(false);
      
      return analysisResponse.data;
    } catch (error) {
      console.error('Error creando incidente:', error);
      setError('Error al crear incidente: ' + error.message);
      setLoading(false);
      return { success: false };
    }
  };

  // ===== ACTUALIZAR ESTADO =====
  const updateIncidentStatus = async (id, newStatus) => {
    try {
      await axios.patch(`${API_BASE}/incidents/${id}/`, {
        resolved: newStatus === 'RESUELTO'
      });
      await loadIncidents();
      setError(null);
    } catch (error) {
      console.error('Error actualizando estado:', error);
      setError('Error al actualizar estado');
    }
  };

  // ===== ELIMINAR INCIDENTE =====
  const deleteIncident = async (id) => {
    try {
      await axios.delete(`${API_BASE}/incidents/${id}/`);
      await loadIncidents();
      setError(null);
    } catch (error) {
      console.error('Error eliminando incidente:', error);
      setError('Error al eliminar incidente');
    }
  };

  // Configuración de gráficos profesionales
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            family: 'Inter',
            size: 12,
            weight: '600'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 41, 0.95)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#3b82f6',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(226, 232, 240, 0.5)',
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11
          }
        }
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11
          }
        }
      }
    }
  };

  // Login Component
  const LoginView = () => (
    <div className="login-container">
      <div className="login-card fade-in">
        <div className="login-header">
          <div className="stats-icon primary mx-auto mb-3">
            🛡️
          </div>
          <h3>CyberShield Pro</h3>
          <p className="text-muted">
            Plataforma Avanzada de Gestión de Incidentes<br/>
            <strong>Potenciado con Inteligencia Artificial</strong>
          </p>
        </div>
        <div className="login-body">
          <div className="d-grid gap-3">
            <button 
              className="btn btn-professional btn-primary py-3" 
              onClick={() => handleLogin('employee@company.com', 'employee')}
            >
              <span style={{fontSize: '1.2rem', marginRight: '0.5rem'}}>👤</span>
              Portal Empleado
            </button>
            <button 
              className="btn btn-professional btn-success py-3" 
              onClick={() => handleLogin('admin@company.com', 'admin')}
            >
              <span style={{fontSize: '1.2rem', marginRight: '0.5rem'}}>👑</span>
              Centro de Comando SOC
            </button>
          </div>
          <div className="mt-4 text-center">
            <small className="text-muted">
              <strong>Desarrollado para PYMES</strong><br/>
              Seguridad Empresarial • Análisis IA • Respuesta Automática
            </small>
          </div>
        </div>
      </div>
    </div>
  );

  // Employee Component
  const EmployeeView = () => {
    const [description, setDescription] = useState('');
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
      if (!description.trim()) return;
      const analysis = await createIncident(description, 'OTRO');
      setResult(analysis);
      setDescription('');
    };

    return (
      <div className="container-fluid p-0">
        <nav className="navbar navbar-expand-lg navbar-professional">
          <div className="container-fluid">
            <span className="navbar-brand">
              <span style={{fontSize: '1.5rem', marginRight: '0.5rem'}}>🛡️</span>
              CyberShield Pro - Portal Empleado
            </span>
            <button className="btn btn-outline-light" onClick={() => {
              setCurrentView('login');
              setIncidents([]);
            }}>
              Cerrar Sesión
            </button>
          </div>
        </nav>

        <div className="container mt-5">
          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {error}
              <button type="button" className="btn-close" onClick={() => setError(null)}></button>
            </div>
          )}

          <div className="row">
            <div className="col-lg-8 mx-auto">
              <div className="card card-professional fade-in">
                <div className="card-header text-center">
                  <div className="stats-icon danger mx-auto mb-3">
                    🚨
                  </div>
                  <h4 className="mb-2">Reportar Incidente de Seguridad</h4>
                  <p className="text-muted mb-0">
                    Análisis inteligente con IA especializada • Respuesta en tiempo real
                  </p>
                </div>
                <div className="card-body">
                  <div className="mb-4">
                    <label className="form-label fw-bold">Descripción Detallada del Incidente:</label>
                    <textarea
                      className="form-control"
                      rows="6"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Describe detalladamente el incidente sospechoso que detectaste...\n\nEjemplos:\n• Recibí un email del CEO solicitando transferencia urgente\n• Se abrió un archivo que bajó la velocidad del sistema\n• Mensaje de WhatsApp con enlace sospechoso del banco"
                      style={{
                        border: '2px solid var(--neutral-200)',
                        borderRadius: 'var(--radius-lg)',
                        fontSize: '1rem',
                        fontFamily: 'Inter, sans-serif'
                      }}
                    />
                  </div>
                  <button 
                    className="btn btn-professional btn-primary w-100 py-3" 
                    onClick={handleAnalyze}
                    disabled={loading || !description.trim()}
                    style={{fontSize: '1.1rem', fontWeight: '700'}}
                  >
                    {loading ? '🔄 Analizando con IA Especializada...' : '🔍 Analizar Amenaza Ahora'}
                  </button>
                </div>
              </div>

              {result && (
                <div className="card card-professional mt-4 fade-in">
                  <div className="card-header">
                    <div className="d-flex align-items-center">
                      <div className="stats-icon primary me-3">
                        📈
                      </div>
                      <div>
                        <h5 className="mb-1">Resultado del Análisis de Amenazas</h5>
                        <small className="text-muted">Procesado por IA Especializada en Ciberseguridad</small>
                      </div>
                    </div>
                  </div>
                  <div className="card-body">
                    {result.success ? (
                      <div>
                        <div className="row mb-4">
                          <div className="col-md-4 text-center">
                            <h6 className="text-muted text-uppercase">Tipo de Amenaza</h6>
                            <span className="badge badge-professional bg-primary" style={{fontSize: '0.9rem', padding: '0.75rem 1.5rem'}}>
                              {result.analysis.threat_type}
                            </span>
                          </div>
                          <div className="col-md-4 text-center">
                            <h6 className="text-muted text-uppercase">Nivel de Criticidad</h6>
                            <span className={`badge badge-professional ${
                              result.analysis.criticality === 'CRITICO' ? 'bg-danger' :
                              result.analysis.criticality === 'ALTO' ? 'bg-warning' : 
                              result.analysis.criticality === 'MEDIO' ? 'bg-info' : 'bg-success'
                            }`} style={{fontSize: '0.9rem', padding: '0.75rem 1.5rem'}}>
                              {result.analysis.criticality}
                            </span>
                          </div>
                          <div className="col-md-4 text-center">
                            <h6 className="text-muted text-uppercase">Confianza IA</h6>
                            <span className="badge badge-professional bg-success" style={{fontSize: '0.9rem', padding: '0.75rem 1.5rem'}}>
                              {Math.round(result.analysis.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="alert" style={{
                          background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1))',
                          border: '1px solid rgba(59, 130, 246, 0.2)',
                          borderRadius: 'var(--radius-lg)'
                        }}>
                          <h6 className="fw-bold">📋 Recomendación del Sistema:</h6>
                          <p className="mb-0" style={{fontSize: '1.1rem', lineHeight: '1.6'}}>
                            {result.analysis.recommendation}
                          </p>
                        </div>
                        
                        <div className="d-flex justify-content-between align-items-center mt-3 pt-3" style={{borderTop: '1px solid var(--neutral-200)'}}>
                          <small className="text-muted">
                            <strong>ID Incidente:</strong> #{result.incident_id}
                          </small>
                          <small className="text-muted">
                            <strong>Timestamp:</strong> {new Date().toLocaleString('es-ES')}
                          </small>
                        </div>
                      </div>
                    ) : (
                      <div className="alert alert-danger">
                        <h6>❌ Error en Análisis</h6>
                        <p className="mb-0">El análisis no se pudo completar. Intenta de nuevo.</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Lista de incidentes del usuario */}
              {incidents.length > 0 && (
                <div className="card card-professional mt-4">
                  <div className="card-header">
                    <h5>📄 Tus Incidentes Reportados</h5>
                    <small className="text-muted">Total: {incidents.length} incidentes</small>
                  </div>
                  <div className="card-body p-0">
                    <div className="list-group list-group-flush">
                      {incidents.map((incident) => (
                        <div key={incident.id} className="list-group-item">
                          <div className="d-flex justify-content-between align-items-start">
                            <div className="flex-grow-1">
                              <h6 className="mb-1">#{incident.id} - {incident.threat_type}</h6>
                              <p className="mb-1 text-muted small">{incident.description.substring(0, 80)}...</p>
                              <small className="text-muted">
                                Creado: {new Date(incident.created_at).toLocaleString('es-ES')}
                              </small>
                            </div>
                            <span className={`badge badge-professional ${
                              incident.criticality === 'CRITICO' ? 'bg-danger' :
                              incident.criticality === 'ALTO' ? 'bg-warning' : 'bg-info'
                            }`}>
                              {incident.criticality}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Admin Dashboard Component
  const AdminView = () => {
    if (!dashboardStats) {
      return (
        <div className="text-center p-5">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p>Cargando datos...</p>
        </div>
      );
    }

    // Datos para gráfico de barras
    const threatBarData = {
      labels: Object.keys(dashboardStats.incidents_by_type || {}),
      datasets: [
        {
          label: 'Incidentes por Tipo',
          data: Object.values(dashboardStats.incidents_by_type || {}),
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(6, 182, 212, 0.8)'
          ],
          borderColor: [
            'rgba(59, 130, 246, 1)',
            'rgba(16, 185, 129, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(239, 68, 68, 1)',
            'rgba(139, 92, 246, 1)',
            'rgba(6, 182, 212, 1)'
          ],
          borderWidth: 2,
          borderRadius: 8,
        }
      ]
    };

    // Datos para gráfico circular
    const threatDoughnutData = {
      labels: Object.keys(dashboardStats.incidents_by_type || {}),
      datasets: [
        {
          data: Object.values(dashboardStats.incidents_by_type || {}),
          backgroundColor: [
            '#3b82f6',
            '#10b981',
            '#f59e0b',
            '#ef4444',
            '#8b5cf6',
            '#06b6d4'
          ],
          borderColor: '#ffffff',
          borderWidth: 3,
          hoverBorderWidth: 4,
        }
      ]
    };

    return (
      <div className="container-fluid p-0">
        <nav className="navbar navbar-expand-lg navbar-professional">
          <div className="container-fluid">
            <span className="navbar-brand">
              <span style={{fontSize: '1.5rem', marginRight: '0.5rem'}}>👑</span>
              CyberShield Pro - Centro de Comando SOC
            </span>
            <button className="btn btn-outline-light" onClick={() => {
              setCurrentView('login');
              setIncidents([]);
              setDashboardStats(null);
            }}>
              Cerrar Sesión
            </button>
          </div>
        </nav>

        <div className="container-fluid mt-4 px-4">
          <div className="fade-in">
            {/* KPIs Cards */}
            <div className="row mb-5">
              <div className="col-xl-3 col-md-6 mb-4">
                <div className="card kpi-card primary">
                  <div className="card-body">
                    <div className="stats-icon primary mx-auto">
                      📈
                    </div>
                    <h5>Total de Incidentes</h5>
                    <h2>{dashboardStats.total_incidents || 0}</h2>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 col-md-6 mb-4">
                <div className="card kpi-card danger">
                  <div className="card-body">
                    <div className="stats-icon danger mx-auto">
                      🚨
                    </div>
                    <h5>Críticos</h5>
                    <h2>{dashboardStats.critical_incidents || 0}</h2>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 col-md-6 mb-4">
                <div className="card kpi-card success">
                  <div className="card-body">
                    <div className="stats-icon success mx-auto">
                      ✅
                    </div>
                    <h5>Resueltos</h5>
                    <h2>{dashboardStats.resolved_incidents || 0}</h2>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 col-md-6 mb-4">
                <div className="card kpi-card warning">
                  <div className="card-body">
                    <div className="stats-icon warning mx-auto">
                      ⏳
                    </div>
                    <h5>Pendientes</h5>
                    <h2>{dashboardStats.pending_incidents || 0}</h2>
                  </div>
                </div>
              </div>
            </div>

            {/* Gráficos */}
            <div className="row mb-5">
              <div className="col-xl-8 mb-4">
                <div className="card card-professional">
                  <div className="card-header">
                    <h5>📈 Distribución de Amenazas por Tipo</h5>
                    <small className="text-muted">Análisis comparativo de incidentes detectados</small>
                  </div>
                  <div className="card-body">
                    <div style={{ height: '350px' }}>
                      {Object.keys(dashboardStats.incidents_by_type || {}).length > 0 ? (
                        <Bar data={threatBarData} options={chartOptions} />
                      ) : (
                        <p className="text-muted text-center">Sin datos aún</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-xl-4 mb-4">
                <div className="card card-professional">
                  <div className="card-header">
                    <h5>🎯 Proporción de Amenazas</h5>
                    <small className="text-muted">Vista circular de incidentes</small>
                  </div>
                  <div className="card-body">
                    <div style={{ height: '350px' }}>
                      {Object.keys(dashboardStats.incidents_by_type || {}).length > 0 ? (
                        <Doughnut data={threatDoughnutData} options={chartOptions} />
                      ) : (
                        <p className="text-muted text-center">Sin datos aún</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabla de incidentes */}
            <div className="card card-professional mb-4">
              <div className="card-header">
                <h5>📋 Registro Completo de Incidentes</h5>
                <small className="text-muted">Total: {incidents.length} incidentes en BD</small>
              </div>
              <div className="card-body p-0">
                {incidents.length > 0 ? (
                  <div className="table-responsive">
                    <table className="table table-professional mb-0">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Tipo de Amenaza</th>
                          <th>Criticidad</th>
                          <th>Descripción</th>
                          <th>Estado</th>
                          <th>Fecha</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {incidents.map((incident) => (
                          <tr key={incident.id}>
                            <td><strong>#{incident.id}</strong></td>
                            <td>{incident.threat_type}</td>
                            <td>
                              <span className={`badge badge-professional ${
                                incident.criticality === 'CRITICO' ? 'bg-danger' :
                                incident.criticality === 'ALTO' ? 'bg-warning' : 'bg-info'
                              }`}>
                                {incident.criticality}
                              </span>
                            </td>
                            <td>{incident.description.substring(0, 50)}...</td>
                            <td>
                              <span className={`badge badge-professional ${incident.resolved ? 'bg-success' : 'bg-warning'}`}>
                                {incident.resolved ? 'RESUELTO' : 'PENDIENTE'}
                              </span>
                            </td>
                            <td>{new Date(incident.created_at).toLocaleDateString('es-ES')}</td>
                            <td>
                              <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => updateIncidentStatus(incident.id, incident.resolved ? 'PENDIENTE' : 'RESUELTO')}
                              >
                                {incident.resolved ? 'Abrir' : 'Resolver'}
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-danger ms-1"
                                onClick={() => deleteIncident(incident.id)}
                              >
                                Eliminar
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-muted text-center p-3">No hay incidentes registrados aún</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Main Render
>>>>>>> 0ac16d3a1f6351a133051af9b8c67e4f08d6cd60
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/report" element={<ReportingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
