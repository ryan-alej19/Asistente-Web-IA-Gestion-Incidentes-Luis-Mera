import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ReportingPage from './pages/ReportingPage';
import './App.css';

// Componente de Ruta Privada: Protege las rutas que requieren autenticación
function PrivateRoute({ children, isAuthenticated }) {
  return isAuthenticated ? children : <Navigate to="/" replace />;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Al cargar la app, verificar si hay usuario en localStorage
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        setCurrentUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  // Manejar login: guardar usuario y cambiar estado
  const handleLogin = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setCurrentUser(userData);
    setIsAuthenticated(true);
  };

  // Manejar logout: limpiar y volver a login
  const handleLogout = () => {
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return (
    <Router>
      <Routes>
        {/* RUTA 1: Login (/) - Solo si NO está autenticado */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          }
        />

        {/* RUTA 2: Dashboard (/dashboard) - Solo si está autenticado */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <Dashboard user={currentUser} onLogout={handleLogout} />
            </PrivateRoute>
          }
        />

        {/* RUTA 3: Reporting (/reporting) - Solo si está autenticado */}
        <Route
          path="/reporting"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <ReportingPage user={currentUser} onLogout={handleLogout} />
            </PrivateRoute>
          }
        />

        {/* RUTA 4: Cualquier otra ruta desconocida → Login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
