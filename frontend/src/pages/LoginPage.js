import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

// Datos de prueba HARDCODEADOS (solo para MVP/demostración)
const TEST_USERS = {
  admin: { password: 'admin123', role: 'admin', name: 'Administrador del Sistema' },
  analista: { password: 'analista123', role: 'analista', name: 'Analista SOC' },
  empleado: { password: 'empleado123', role: 'empleado', name: 'Empleado' }
};

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simular validación (en el futuro será llamada al backend)
    setTimeout(() => {
      if (!username || !password) {
        setError('Usuario y contraseña requeridos');
        setLoading(false);
        return;
      }

      const user = TEST_USERS[username];

      if (user && user.password === password) {
        // ✅ LOGIN EXITOSO
        const userData = {
          username,
          role: user.role,
          name: user.name,
          loginTime: new Date().toISOString()
        };

        // 🔑 LLAMAR A onLogin PROP (AQUÍ ESTABA EL PROBLEMA)
        onLogin(userData);

        // Redirigir al dashboard
        navigate('/dashboard');
      } else {
        setError('Usuario o contraseña incorrectos');
        setLoading(false);
      }
    }, 500);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <span className="lock-icon">🔒</span>
          <h1>Gestor de Incidentes de Seguridad</h1>
          <p className="subtitle">Sistema de gestión con autenticación por roles</p>
        </div>

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="username">Usuario</label>
            <input
              type="text"
              id="username"
              placeholder="Ingresa tu usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value.toLowerCase())}
              disabled={loading}
              autoFocus
            />
            <small className="hint">Ej: admin, analista, empleado</small>
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              placeholder="Ingresa tu contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">❌ {error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Validando...' : 'Iniciar Sesión'}
          </button>
        </form>

        {/* SECCIÓN DE CREDENCIALES DE PRUEBA */}
        <div className="credentials-info">
          <h3>📋 Credenciales de Prueba</h3>
          <div className="credentials-grid">
            {/* Admin */}
            <div className="credential-card">
              <div className="card-icon">👨‍💼</div>
              <strong>Administrador</strong>
              <div className="cred-item">
                <span className="label">Usuario:</span>
                <code>admin</code>
              </div>
              <div className="cred-item">
                <span className="label">Contraseña:</span>
                <code>admin123</code>
              </div>
              <span className="role-badge admin">🔐 Admin</span>
            </div>

            {/* Analista */}
            <div className="credential-card">
              <div className="card-icon">🔍</div>
              <strong>Analista SOC</strong>
              <div className="cred-item">
                <span className="label">Usuario:</span>
                <code>analista</code>
              </div>
              <div className="cred-item">
                <span className="label">Contraseña:</span>
                <code>analista123</code>
              </div>
              <span className="role-badge analista">🛡️ Analista</span>
            </div>

            {/* Empleado */}
            <div className="credential-card">
              <div className="card-icon">👤</div>
              <strong>Empleado</strong>
              <div className="cred-item">
                <span className="label">Usuario:</span>
                <code>empleado</code>
              </div>
              <div className="cred-item">
                <span className="label">Contraseña:</span>
                <code>empleado123</code>
              </div>
              <span className="role-badge empleado">✅ Empleado</span>
            </div>
          </div>
          <div className="info-box">
            <strong>ℹ️ Nota:</strong> Esta es una demostración. En producción, la autenticación 
            se conectaría a un backend con base de datos real.
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
