import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Bar, Doughnut } from 'react-chartjs-2';
import axios from 'axios';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/dashboard/stats/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error:', err);
      // Datos de prueba
      setStats({
        role: 'admin',
        total: 127,
        critical: 8,
        high: 23,
        medium: 45,
        low: 51,
        open: 34,
        in_progress: 56,
        closed: 37,
        average_confidence: 87.5,
        admin_extra: {
          total_users: 15,
          total_analysts: 3,
          total_employees: 11,
          critical_unresolved: 8
        }
      });
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) return <div className="dashboard-loading">Cargando...</div>;
  if (!stats) return <div>Error cargando datos</div>;

  const severityData = {
    labels: ['Crítico', 'Alto', 'Medio', 'Bajo'],
    datasets: [{
      label: 'Incidentes',
      data: [stats.critical || 0, stats.high || 0, stats.medium || 0, stats.low || 0],
      backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e'],
    }]
  };

  const statusData = {
    labels: ['Abiertos', 'En Progreso', 'Cerrados'],
    datasets: [{
      data: [stats.open || 0, stats.in_progress || 0, stats.closed || 0],
      backgroundColor: ['#3b82f6', '#8b5cf6', '#22c55e'],
    }]
  };

  return (
    <div className="dashboard">
      {/* HEADER */}
      <div className="dashboard-header">
        <div className="header-content">
          <div>
            <h1 className="dashboard-title">👑 Dashboard de Administrador</h1>
            <p className="welcome-message">
              ¡Hola, <strong>{user?.username}</strong>! | Rol: Administrador
            </p>
            <p className="role-description">
              Vista completa del sistema - Gestiona usuarios, incidentes y configuración
            </p>
          </div>
          <button onClick={handleLogout} className="btn-logout">
            🚪 Cerrar Sesión
          </button>
        </div>
      </div>

      {/* TARJETAS PRINCIPALES */}
      <div className="stats-grid">
        <div className="stat-card stat-blue">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <p className="stat-label">Total Incidentes</p>
            <p className="stat-value">{stats.total || 0}</p>
          </div>
        </div>

        <div className="stat-card stat-red">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <p className="stat-label">Críticos Pendientes</p>
            <p className="stat-value">{stats.critical || 0}</p>
          </div>
        </div>

        <div className="stat-card stat-green">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <p className="stat-label">Usuarios Activos</p>
            <p className="stat-value">{stats.admin_extra?.total_users || 0}</p>
          </div>
        </div>
      </div>

      {/* PANEL ADMIN */}
      <div className="admin-section">
        <h2 className="section-title">⚙️ Información del Sistema</h2>
        <div className="admin-grid">
          <div className="admin-card">
            <p className="admin-label">Total Usuarios</p>
            <p className="admin-value">{stats.admin_extra?.total_users || 0}</p>
          </div>
          <div className="admin-card">
            <p className="admin-label">Analistas</p>
            <p className="admin-value">{stats.admin_extra?.total_analysts || 0}</p>
          </div>
          <div className="admin-card">
            <p className="admin-label">Empleados</p>
            <p className="admin-value">{stats.admin_extra?.total_employees || 0}</p>
          </div>
          <div className="admin-card">
            <p className="admin-label">🚨 Críticos Abiertos</p>
            <p className="admin-value admin-critical">{stats.admin_extra?.critical_unresolved || 0}</p>
          </div>
        </div>
      </div>

      {/* GRÁFICOS */}
      <div className="charts-grid">
        <div className="chart-container">
          <h3>📈 Incidentes por Severidad</h3>
          <div className="chart-wrapper">
            <Bar 
              data={severityData} 
              options={{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                  legend: { 
                    display: true,
                    position: 'top'
                  }
                }
              }} 
            />
          </div>
        </div>

        <div className="chart-container">
          <h3>👥 Usuarios por Rol</h3>
          <div className="chart-wrapper">
            <Doughnut 
              data={{
                labels: ['Analistas', 'Empleados'],
                datasets: [{
                  data: [stats.admin_extra?.total_analysts || 0, stats.admin_extra?.total_employees || 0],
                  backgroundColor: ['#3b82f6', '#10b981'],
                }]
              }}
              options={{ 
                responsive: true, 
                maintainAspectRatio: false 
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
