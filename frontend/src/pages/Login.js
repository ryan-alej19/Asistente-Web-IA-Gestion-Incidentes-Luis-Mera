import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Lock, LogIn, AlertOctagon, ShieldCheck, Eye, EyeOff, Loader2 } from 'lucide-react';
import API_URL from '../config/api';

const Login = ({ setAuth, setRole }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post(`${API_URL}/api/auth/token/`, {
                username,
                password
            });

            const { token, role } = response.data;

            localStorage.setItem('token', token);
            localStorage.setItem('role', role);
            if (response.data.user_id) localStorage.setItem('user_id', response.data.user_id);
            if (username) localStorage.setItem('username', username);

            setAuth(true);
            setRole(role);

            // Simular un pequeño delay para la animación de salida
            setTimeout(() => {
                if (role === 'analyst' || role === 'admin') {
                    navigate('/analyst');
                } else {
                    navigate('/employee');
                }
            }, 500);

        } catch (err) {
            console.error(err);
            setError('Credenciales incorrectas o error de conexión');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4 overflow-hidden relative">

            {/* Background Decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] opacity-30 animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px] opacity-30 animate-pulse" style={{ animationDelay: '2s' }} />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md z-10"
            >
                <div className="bg-surface border border-border shadow-2xl rounded-2xl overflow-hidden backdrop-blur-xl">

                    {/* Header with Logo */}
                    <div className="p-8 pb-0 text-center relative z-10">
                        <motion.div
                            initial={{ scale: 0.5, opacity: 0, y: -20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            transition={{ type: "spring", stiffness: 260, damping: 20, delay: 0.1 }}
                            className="relative mx-auto w-40 h-40 mb-6 group cursor-pointer perspective-1000"
                        >
                            <div className="absolute inset-0 bg-primary/30 rounded-full blur-2xl group-hover:bg-primary/50 transition-all duration-500 animate-pulse" />
                            <div className="relative bg-white w-full h-full rounded-3xl flex items-center justify-center p-6 shadow-2xl shadow-primary/20 border-4 border-white/50 backdrop-blur-sm transform transition-transform duration-500 hover:scale-105 hover:rotate-3">
                                <img
                                    src="/assets/logo_tecnicontrol.jpg"
                                    alt="Tecnicontrol Logo"
                                    className="w-full h-full object-contain filter drop-shadow-sm"
                                />
                                {/* Shine effect */}
                                <div className="absolute inset-0 rounded-3xl bg-gradient-to-tr from-white/0 via-white/40 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
                                    style={{ transform: 'translateZ(1px)' }}
                                />
                            </div>
                        </motion.div>
                        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Bienvenido</h1>
                        <p className="text-gray-400 text-sm">
                            Sistema de Ciberseguridad <span className="text-primary font-bold">Tecnicontrol</span>
                        </p>
                    </div>

                    {/* Form */}
                    <div className="p-8">
                        <form onSubmit={handleLogin} className="space-y-6">

                            {/* Username Input */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300 ml-1">Usuario</label>
                                <div className="relative group">
                                    <User className="absolute left-3 top-3.5 w-5 h-5 text-gray-500 group-focus-within:text-primary transition-colors" />
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        className="w-full bg-background border border-border text-white pl-10 pr-4 py-3 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary/50 outline-none transition-all placeholder-gray-600"
                                        placeholder="Ingrese su usuario"
                                        required
                                    />
                                </div>
                            </div>

                            {/* Password Input */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300 ml-1">Contraseña</label>
                                <div className="relative group">
                                    <Lock className="absolute left-3 top-3.5 w-5 h-5 text-gray-500 group-focus-within:text-primary transition-colors" />
                                    <input
                                        type={showPassword ? "text" : "password"}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full bg-background border border-border text-white pl-10 pr-12 py-3 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary/50 outline-none transition-all placeholder-gray-600"
                                        placeholder="••••••••"
                                        required
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-3.5 text-gray-500 hover:text-white transition-colors"
                                    >
                                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                            </div>

                            {/* Error Message */}
                            <AnimatePresence>
                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="bg-danger/10 border border-danger/20 rounded-lg p-3 flex items-center gap-3 text-danger text-sm"
                                    >
                                        <AlertOctagon className="w-5 h-5 flex-shrink-0" />
                                        <p>{error}</p>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-primary hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3.5 rounded-xl shadow-lg shadow-primary/25 transition-all flex items-center justify-center gap-2 mt-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Autenticando...</span>
                                    </>
                                ) : (
                                    <>
                                        <LogIn className="w-5 h-5" />
                                        <span>Iniciar Sesión</span>
                                    </>
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Footer */}
                    <div className="px-8 pb-8 text-center">
                        <p className="text-xs text-center text-gray-500 border-t border-border pt-6">
                            Protegido por <span className="text-gray-400 font-medium">Tecnicontrol Security Ops</span> v2.5
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
