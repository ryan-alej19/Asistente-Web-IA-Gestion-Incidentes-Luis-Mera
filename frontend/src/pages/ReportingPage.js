import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import IncidentReporter from '../components/IncidentReporter';
import './ReportingPage.css';

function ReportingPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="reporting-page">
      {/* Header */}
      <div className="reporting-header">
        <div>
          <h1>📝 Centro de Reportes de Seguridad</h1>
          <p className="text-gray-600">Reporta incidentes de ciberseguridad aquí</p>
        </div>
        <div className="reporting-actions">
          <button 
            onClick={() => navigate('/dashboard')}
            className="btn-secondary"
          >
            🏠 Volver al Dashboard
          </button>
          <button 
            onClick={handleLogout}
            className="btn-logout"
          >
            🚪 Cerrar Sesión
          </button>
        </div>
      </div>

      {/* Formulario de Reporte */}
      <IncidentReporter />
    </div>
  );
}

export default ReportingPage;
