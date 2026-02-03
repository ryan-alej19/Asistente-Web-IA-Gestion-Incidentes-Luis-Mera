import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import EmployeeDashboard from './pages/EmployeeDashboard';
import AnalystDashboard from './pages/AnalystDashboard';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    if (token) {
      setIsAuthenticated(true);
      setUserRole(role);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="loading-screen">Cargando sistema...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          !isAuthenticated ?
            <Login setAuth={setIsAuthenticated} setRole={setUserRole} /> :
            <Navigate to={userRole === 'analyst' || userRole === 'admin' ? "/analyst" : "/employee"} />
        } />

        <Route path="/employee" element={
          isAuthenticated && userRole === 'employee' ?
            <EmployeeDashboard /> :
            <Navigate to="/login" />
        } />

        <Route path="/analyst" element={
          isAuthenticated && (userRole === 'analyst' || userRole === 'admin') ?
            <AnalystDashboard /> :
            <Navigate to="/login" />
        } />

        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
