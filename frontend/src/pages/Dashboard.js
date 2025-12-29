/**
 * Dashboard principal
 * Muestra estadísticas e incidentes en tiempo real
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import '../styles/Dashboard.css';
import incidentService from '../services/incidentService';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cargar datos al montar componente
  useEffect(() => {
    fetchDashboardData();
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Obtener estadísticas
      const statsData = await incidentService.getStatistics();
      setStats(statsData);
      
      // Obtener incidentes recientes
      const incidentsData = await incidentService.getRecentIncidents();
      setIncidents(Array.isArray(incidentsData) ? incidentsData : incidentsData.results || []);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Error al cargar datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !stats) {
    return <div className="dashboard-loading">Cargando dashboard...</div>;
  }

  // Preparar datos para gráfica de severidad
  const severityData = {
    labels: ['BAJO', 'MEDIO', 'ALTO', 'CRÍTICO'],
    datasets: [
      {
        label: 'Incidentes por Severidad',
        data: [
          stats?.by_severity?.find(s => s.severity === 'low')?.count || 0,
          stats?.by_severity?.find(s => s.severity === 'medium')?.count || 0,
          stats?.by_severity?.find(s => s.severity === 'high')?.count || 0,
          stats?.by_severity?.find(s => s.severity === 'critical')?.count || 0,
        ],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#dc2626'],
        borderColor: ['#059669', '#d97706', '#dc2626', '#991b1b'],
        borderWidth: 1,
      },
    ],
  };

  // Preparar datos para gráfica de estado
  const statusData = {
    labels: ['Nuevos', 'En revisión', 'En progreso', 'Resueltos'],
    datasets: [
      {
        label: 'Incidentes por Estado',
        data: [
          stats?.by_status?.find(s => s.status === 'new')?.count || 0,
          stats?.by_status?.find(s => s.status === 'under_review')?.count || 0,
          stats?.by_status?.find(s => s.status === 'in_progress')?.count || 0,
          stats?.by_status?.find(s => s.status === 'resolved')?.count || 0,
        ],
        backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981'],
        borderColor: ['#1e40af', '#6d28d9', '#be185d', '#059669'],
        borderWidth: 1,
      },
    ],
  };

  // Preparar datos para gráfica de tipo de amenaza
  const threatData = {
    labels: Object.keys(stats?.by_type || {}),
    datasets: [
      {
        label: 'Incidentes por Tipo',
        data: Object.values(stats?.by_type || {}),
        backgroundColor: [
          '#f59e0b',
          '#ef4444',
          '#3b82f6',
          '#8b5cf6',
          '#10b981',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        font: {
          size: 14,
        },
      },
    },
  };

  return (
    <div className="dashboard">
      <h1 className="dashboard-title">📊 Dashboard de Seguridad</h1>

      {error && <div className="alert alert-error">{error}</div>}

      {/* ESTADÍSTICAS PRINCIPALES */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-label">Total Incidentes</div>
            <div className="stat-value">{stats?.total_incidents || 0}</div>
          </div>
        </div>

        <div className="stat-card stat-critical">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <div className="stat-label">Críticos Sin Resolver</div>
            <div className="stat-value">{stats?.unresolved_critical || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-label">Confianza Promedio</div>
            <div className="stat-value">{stats?.average_confidence || 0}%</div>
          </div>
        </div>
      </div>

      {/* GRÁFICAS */}
      <div className="charts-grid">
        <div className="chart-container">
          <h3>Incidentes por Severidad</h3>
          <Bar data={severityData} options={chartOptions} />
        </div>

        <div className="chart-container">
          <h3>Incidentes por Estado</h3>
          <Doughnut data={statusData} options={chartOptions} />
        </div>

        <div className="chart-container">
          <h3>Incidentes por Tipo</h3>
          <Doughnut data={threatData} options={chartOptions} />
        </div>
      </div>

      {/* INCIDENTES RECIENTES */}
      <div className="recent-incidents">
        <h3>🔔 Incidentes Recientes (Últimas 24h)</h3>
        
        {incidents.length === 0 ? (
          <p className="no-incidents">No hay incidentes en las últimas 24 horas</p>
        ) : (
          <div className="incidents-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Título</th>
                  <th>Severidad</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Confianza</th>
                </tr>
              </thead>
              <tbody>
                {incidents.slice(0, 10).map((incident) => (
                  <tr key={incident.id}>
                    <td>#{incident.id}</td>
                    <td>{incident.title}</td>
                    <td>
                      <span className={`badge badge-${incident.severity}`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td>{incident.threat_type}</td>
                    <td>
                      <span className={`status status-${incident.status}`}>
                        {incident.status}
                      </span>
                    </td>
                    <td>{Math.round((incident.confidence || 0) * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <button onClick={fetchDashboardData} className="btn-refresh">
        🔄 Actualizar Datos
      </button>
    </div>
  );
};

export default Dashboard;
