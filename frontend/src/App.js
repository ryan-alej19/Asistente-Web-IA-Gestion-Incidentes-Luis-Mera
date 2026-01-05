/**
 * 🛡️ APP PRINCIPAL - TESIS CIBERSEGURIDAD
 * Ryan Gallegos Mera - PUCESI
 * Última actualización: 03 de Enero, 2026
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ReportingPage from './pages/ReportingPage';
import CreateIncident from './components/CreateIncident'; // ← NUEVA LÍNEA
import './App.css';


function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Ruta de login */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Dashboard principal */}
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Página de reportes */}
            <Route path="/reportes" element={<ReportingPage />} />
            
            {/* NUEVA RUTA: Crear incidente con IA */}
            <Route path="/crear-incidente" element={<CreateIncident />} />
            
            {/* Redirigir a login por defecto */}
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
