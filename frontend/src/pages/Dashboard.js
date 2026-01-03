import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AdminDashboard from './AdminDashboard';
import AnalystDashboard from './AnalystDashboard';
import EmployeeDashboard from './EmployeeDashboard';

function Dashboard() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    if (!loading && !user) {
      navigate('/');
    } else if (user) {
      setUserRole(user?.role);
    }
  }, [user, loading, navigate]);

  if (loading) {
    return <div className="dashboard-loading"><p>Cargando...</p></div>;
  }

  if (!user) {
    return null;
  }

  // Renderiza dashboard según el rol
  switch (userRole) {
    case 'admin':
      return <AdminDashboard />;
    case 'analyst':
      return <AnalystDashboard />;
    case 'employee':
      return <EmployeeDashboard />;
    default:
      return <div>Rol no reconocido</div>;
  }
}

export default Dashboard;
