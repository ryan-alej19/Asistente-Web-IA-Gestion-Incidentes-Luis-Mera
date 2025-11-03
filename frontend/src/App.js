import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import './Professional.css';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [currentView, setCurrentView] = useState('login');
  const [userRole, setUserRole] = useState('');
  const [incidents, setIncidents] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Función login
  const handleLogin = (email, role) => {
    setUserRole(role);
    if (role === 'admin') {
      setCurrentView('admin');
      loadDashboardData();
    } else {
      setCurrentView('employee');
    }
    loadIncidents();
  };

  // Cargar datos del dashboard
  const loadDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/dashboard/stats/');
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error cargando dashboard:', error);
    }
  };

  // Cargar incidentes
  const loadIncidents = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/incidents/');
      setIncidents(response.data);
    } catch (error) {
      console.error('Error cargando incidentes:', error);
    }
  };

  // Análisis IA
  const analyzeIncident = async (description) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/incidents/analyze/', {
        description: description
      });
      setLoading(false);
      return response.data;
    } catch (error) {
      console.error('Error en análisis:', error);
      setLoading(false);
      return { success: false, analysis: { recommendation: "Error en análisis automático. Contactar soporte técnico." } };
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

  // Login Component - PREMIUM
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

  // Employee Component - PREMIUM
  const EmployeeView = () => {
    const [description, setDescription] = useState('');
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
      if (!description.trim()) return;
      const analysis = await analyzeIncident(description);
      setResult(analysis);
    };

    return (
      <div className="container-fluid p-0">
        <nav className="navbar navbar-expand-lg navbar-professional">
          <div className="container-fluid">
            <span className="navbar-brand">
              <span style={{fontSize: '1.5rem', marginRight: '0.5rem'}}>🛡️</span>
              CyberShield Pro - Portal Empleado
            </span>
            <button className="btn btn-outline-light" onClick={() => setCurrentView('login')}>
              Cerrar Sesión
            </button>
          </div>
        </nav>

        <div className="container mt-5">
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
                      placeholder="Describe detalladamente el incidente sospechoso que detectaste...

Ejemplos:
• Recibí un email del CEO solicitando transferencia urgente
• Se abrió un archivo que bajó la velocidad del sistema
• Mensaje de WhatsApp con enlace sospechoso del banco"
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
                        📊
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
                              result.analysis.criticality === 'CRÍTICO' ? 'bg-danger' :
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
                        <p className="mb-0">{result.analysis.recommendation}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Admin Dashboard Component - PREMIUM CON GRÁFICOS
  const AdminView = () => {
    if (!dashboardStats) return null;

    // Datos para gráfico de barras
    const threatBarData = {
      labels: Object.keys(dashboardStats.incidents_by_type),
      datasets: [
        {
          label: 'Incidentes por Tipo',
          data: Object.values(dashboardStats.incidents_by_type),
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
      labels: Object.keys(dashboardStats.incidents_by_type),
      datasets: [
        {
          data: Object.values(dashboardStats.incidents_by_type),
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

    // Datos para gráfico de línea temporal
    const timelineData = {
      labels: dashboardStats.incidents_by_month.map(item => item.month),
      datasets: [
        {
          label: 'Tendencia de Incidentes',
          data: dashboardStats.incidents_by_month.map(item => item.count),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 3,
          pointRadius: 8,
          pointHoverRadius: 12,
          fill: true,
          tension: 0.4
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
            <button className="btn btn-outline-light" onClick={() => setCurrentView('login')}>
              Cerrar Sesión
            </button>
          </div>
        </nav>

        <div className="container-fluid mt-4 px-4">
          <div className="fade-in">
            {/* KPIs Cards - PREMIUM */}
            <div className="row mb-5">
              <div className="col-xl-3 col-md-6 mb-4">
                <div className="card kpi-card primary">
                  <div className="card-body">
                    <div className="stats-icon primary mx-auto">
                      📊
                    </div>
                    <h5>Total de Incidentes</h5>
                    <h2>{dashboardStats.total_incidents}</h2>
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
                    <h2>{dashboardStats.critical_incidents}</h2>
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
                    <h2>{dashboardStats.resolved_incidents}</h2>
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
                    <h2>{dashboardStats.pending_incidents}</h2>
                  </div>
                </div>
              </div>
            </div>

            {/* Gráficos Profesionales */}
            <div className="row mb-5">
              <div className="col-xl-8 mb-4">
                <div className="card card-professional">
                  <div className="card-header">
                    <h5>📊 Distribución de Amenazas por Tipo</h5>
                    <small className="text-muted">Análisis comparativo de incidentes detectados</small>
                  </div>
                  <div className="card-body">
                    <div style={{ height: '350px' }}>
                      <Bar data={threatBarData} options={chartOptions} />
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
                      <Doughnut data={threatDoughnutData} options={chartOptions} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tendencia Temporal */}
            <div className="row mb-5">
              <div className="col-12 mb-4">
                <div className="card card-professional">
                  <div className="card-header">
                    <h5>📈 Tendencia de Incidentes - Últimos Meses</h5>
                    <small className="text-muted">Evolución temporal de amenazas detectadas</small>
                  </div>
                  <div className="card-body">
                    <div style={{ height: '300px' }}>
                      <Line data={timelineData} options={chartOptions} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Actividad Reciente */}
            <div className="row mb-4">
              <div className="col-lg-6 mb-4">
                <div className="card card-professional">
                  <div className="card-header">
                    <h5>⚡ Actividad Reciente</h5>
                    <small className="text-muted">Últimos incidentes procesados</small>
                  </div>
                  <div className="card-body">
                    {dashboardStats.recent_activity.map((activity, index) => (
                      <div key={activity.id} className="d-flex justify-content-between align-items-center mb-3 p-3" 
                           style={{
                             background: 'var(--neutral-100)', 
                             borderRadius: 'var(--radius-md)',
                             border: '1px solid var(--neutral-200)'
                           }}>
                        <div>
                          <strong>#{activity.id}</strong>
                          <div className="text-muted small">{activity.type}</div>
                          <div className="text-muted smaller">{activity.date}</div>
                        </div>
                        <span className={`badge badge-professional ${
                          activity.status === 'RESUELTO' ? 'bg-success' : 
                          activity.status === 'PENDIENTE' ? 'bg-warning' : 'bg-info'
                        }`}>
                          {activity.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="col-lg-6 mb-4">
                <div className="card card-professional">
                  <div className="card-header">
                    <h5>🏆 Métricas de Rendimiento</h5>
                    <small className="text-muted">Indicadores clave del sistema</small>
                  </div>
                  <div className="card-body">
                    <div className="row text-center">
                      <div className="col-6 mb-3">
                        <h3 className="text-primary">98.5%</h3>
                        <small className="text-muted">Precisión IA</small>
                      </div>
                      <div className="col-6 mb-3">
                        <h3 className="text-success">2.3s</h3>
                        <small className="text-muted">Tiempo Respuesta</small>
                      </div>
                      <div className="col-6">
                        <h3 className="text-warning">24/7</h3>
                        <small className="text-muted">Monitoreo</small>
                      </div>
                      <div className="col-6">
                        <h3 className="text-info">99.9%</h3>
                        <small className="text-muted">Uptime</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabla Premium */}
            <div className="card card-professional mb-4">
              <div className="card-header">
                <h5>📋 Registro Completo de Incidentes</h5>
                <small className="text-muted">Historial detallado de todos los eventos de seguridad</small>
              </div>
              <div className="card-body p-0">
                <div className="table-responsive">
                  <table className="table table-professional mb-0">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Tipo de Amenaza</th>
                        <th>Criticidad</th>
                        <th>Estado</th>
                        <th>Fecha</th>
                        <th>Confianza IA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {incidents.map((incident) => (
                        <tr key={incident.id}>
                          <td><strong>#{incident.id}</strong></td>
                          <td>
                            <span className="fw-semibold">{incident.threat_type}</span>
                          </td>
                          <td>
                            <span className={`badge badge-professional ${
                              incident.criticality === 'CRÍTICO' ? 'bg-danger' :
                              incident.criticality === 'ALTO' ? 'bg-warning' : 'bg-info'
                            }`}>
                              {incident.criticality}
                            </span>
                          </td>
                          <td>
                            <span className={`badge badge-professional ${incident.resolved ? 'bg-success' : 'bg-warning'}`}>
                              {incident.resolved ? 'RESUELTO' : 'PENDIENTE'}
                            </span>
                          </td>
                          <td>{new Date(incident.created_at).toLocaleDateString('es-ES')}</td>
                          <td>
                            <strong className="text-success">
                              {Math.round(incident.confidence_score * 100)}%
                            </strong>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Main Render
  return (
    <div className="App">
      {currentView === 'login' && <LoginView />}
      {currentView === 'employee' && <EmployeeView />}
      {currentView === 'admin' && <AdminView />}
    </div>
  );
}

export default App;
