import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ReportingPage from './pages/ReportingPage';
import './App.css';

// Componente de Ruta Privada: Protege las rutas que requieren autenticación
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return user ? children : <Navigate to="/" replace />;
}

// Componente de Ruta Pública: Solo accesible si NO estás autenticado
function PublicRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return user ? <Navigate to="/dashboard" replace /> : children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* RUTA 1: Login (/) - Solo si NO está autenticado */}
      <Route
        path="/"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      {/* RUTA 2: Dashboard (/dashboard) - Solo si está autenticado */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />

      {/* RUTA 3: Reporting (/reporting) - Solo si está autenticado */}
      <Route
        path="/reporting"
        element={
          <PrivateRoute>
            <ReportingPage />
          </PrivateRoute>
        }
      />

      {/* RUTA 4: Cualquier otra ruta desconocida → Login */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
