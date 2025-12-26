import React, { useState } from 'react';

function Login({ onLoginSuccess }) {
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://localhost:8000/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            if (!response.ok) {
                throw new Error('Login fallido');
            }

            const data = await response.json();

            // Guardar los tokens en localStorage
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);

            console.log('✅ Login exitoso:', data);
            
            if (onLoginSuccess) {
                onLoginSuccess();
            }

        } catch (err) {
            setError(`❌ Error: ${err.message}`);
            console.error('Error en login:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            maxWidth: '400px',
            margin: '50px auto',
            padding: '20px',
            border: '1px solid #ccc',
            borderRadius: '8px',
            backgroundColor: '#f9f9f9'
        }}>
            <h2>🔐 Login - Portal de Seguridad</h2>
            
            {error && (
                <div style={{
                    backgroundColor: '#fee',
                    color: '#c33',
                    padding: '10px',
                    borderRadius: '4px',
                    marginBottom: '15px'
                }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleLogin}>
                <div style={{ marginBottom: '15px' }}>
                    <label>Usuario:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '8px',
                            marginTop: '5px',
                            borderRadius: '4px',
                            border: '1px solid #ccc',
                            boxSizing: 'border-box'
                        }}
                        disabled={loading}
                    />
                </div>

                <div style={{ marginBottom: '15px' }}>
                    <label>Contraseña:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '8px',
                            marginTop: '5px',
                            borderRadius: '4px',
                            border: '1px solid #ccc',
                            boxSizing: 'border-box'
                        }}
                        disabled={loading}
                    />
                </div>

                <button
                    type="submit"
                    style={{
                        width: '100%',
                        padding: '10px',
                        backgroundColor: '#5a5ac4',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        opacity: loading ? 0.6 : 1
                    }}
                    disabled={loading}
                >
                    {loading ? '⏳ Iniciando sesión...' : '🔓 Iniciar Sesión'}
                </button>
            </form>

            <p style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
                💡 Por defecto: usuario <strong>admin</strong> / contraseña <strong>admin</strong>
            </p>
        </div>
    );
}

export default Login;
