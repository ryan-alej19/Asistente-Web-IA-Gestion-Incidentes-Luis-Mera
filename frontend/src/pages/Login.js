import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = ({ setAuth, setRole }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Usar endpoint directo
            const response = await axios.post('http://localhost:8000/api/auth/token/', {
                username,
                password
            });

            const { token, role } = response.data;

            localStorage.setItem('token', token);
            localStorage.setItem('role', role);

            setAuth(true);
            setRole(role);

            if (role === 'analyst' || role === 'admin') {
                navigate('/analyst');
            } else {
                navigate('/employee');
            }

        } catch (err) {
            console.error(err);
            setError('Credenciales incorrectas o error de conexión');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="card" style={{ width: '400px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    Sistema de Ciberseguridad
                    <br />
                    <span style={{ fontSize: '1rem', color: '#94a3b8', fontWeight: 'normal' }}>
                        Talleres Luis Mera
                    </span>
                </h2>

                <form onSubmit={handleLogin}>
                    <div className="input-group">
                        <label>Usuario</label>
                        <input
                            type="text"
                            className="input-field"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label>Contraseña</label>
                        <input
                            type="password"
                            className="input-field"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {error && (
                        <div style={{ color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center' }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%' }}
                        disabled={loading}
                    >
                        {loading ? 'Ingresando...' : 'Iniciar Sesión'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
