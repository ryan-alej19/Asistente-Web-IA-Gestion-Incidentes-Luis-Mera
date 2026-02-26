import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
    LayoutDashboard, Users, LogOut, Search, Filter, ChevronDown, ShieldAlert
} from 'lucide-react';
import StatisticsCards from '../components/analyst/StatisticsCards';
import IncidentsTable from '../components/analyst/IncidentsTable';
import IncidentDetailModal from '../components/analyst/IncidentDetailModal';
import ChangeStateModal from '../components/analyst/ChangeStateModal';
import UsersTable from '../components/admin/UsersTable';
import LoginAttemptsTable from '../components/admin/LoginAttemptsTable';
import API_URL from '../config/api';

const AdminDashboard = () => {
    // Shared State
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'users'

    // Dashboard/Incidents State
    const [stats, setStats] = useState(null);
    const [incidents, setIncidents] = useState([]);
    const [filterRisk, setFilterRisk] = useState('');
    const [filterType, setFilterType] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');

    // Users State
    const [users, setUsers] = useState([]);

    // Audit State
    const [loginAttempts, setLoginAttempts] = useState([]);

    // Modal State
    const [selectedIncident, setSelectedIncident] = useState(null);
    const [incidentToChange, setIncidentToChange] = useState(null);
    const [showDetailModal, setShowDetailModal] = useState(false);
    const [showChangeStateModal, setShowChangeStateModal] = useState(false);

    useEffect(() => {
        fetchStatsAndUsers();
    }, []);

    // Initial Fetch
    useEffect(() => {
        fetchIncidents();
    }, []); // Run once on mount

    // Debounce Search - ONLY for Search if we wanted server side, but we are client side now.
    // So we don't need this effect for filtering anymore.

    const fetchStatsAndUsers = async () => {
        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Token ${token}` } };

            // Cargar estadísticas y usuarios y logs en paralelo
            const [statsRes, usersRes, attemptsRes] = await Promise.all([
                axios.get(`${API_URL}/api/incidents/stats/`, config),
                axios.get(`${API_URL}/api/users/list/`, config),
                axios.get(`${API_URL}/api/users/login-attempts/`, config)
            ]);
            setStats(statsRes.data);
            setUsers(usersRes.data);
            setLoginAttempts(attemptsRes.data.results);
        } catch (err) {
            console.error("Error cargando estadísticas y usuarios:", err);
        }
    };

    const fetchIncidents = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const config = {
                headers: { Authorization: `Token ${token}` }
                // Removed server-side params to use client-side filtering (Consistent with Analyst)
            };

            const response = await axios.get(`${API_URL}/api/incidents/list/`, config);
            setIncidents(response.data.results);

        } catch (err) {
            console.error("Error fetching incidents:", err);
            setError("Error al cargar incidentes.");
        } finally {
            setLoading(false);
        }
    };

    // Filter Logic (Client Side)
    const filteredIncidents = incidents.filter(inc => {
        // Search
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            const matchesId = inc.id.toString().includes(term);
            const matchesDesc = inc.description?.toLowerCase().includes(term);
            const matchesRisk = inc.risk_level?.toLowerCase().includes(term);
            const matchesType = inc.incident_type?.toLowerCase().includes(term);
            const matchesUrl = inc.url?.toLowerCase().includes(term);
            const matchesFile = inc.attached_file?.toLowerCase().includes(term);

            if (!matchesId && !matchesDesc && !matchesRisk && !matchesType && !matchesUrl && !matchesFile) {
                return false;
            }
        }

        // Filter by Type
        if (filterType !== 'all') {
            const type = inc.incident_type?.toLowerCase() || '';
            if (type !== filterType.toLowerCase()) return false;
        }

        // Filter by Risk
        if (filterRisk && inc.risk_level !== filterRisk) return false;

        return true;
    });

    console.log("AdminDashboard Render:", {
        total: incidents.length,
        filtered: filteredIncidents.length,
        filterType,
        filterRisk
    });

    // Reload all data (e.g. after update)
    const reloadAll = () => {
        fetchStatsAndUsers();
        fetchIncidents();
    };

    // User Management Handlers
    const handleToggleStatus = async (userId) => {
        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Token ${token}` } };
            await axios.patch(`${API_URL}/api/users/${userId}/toggle_status/`, {}, config);
            fetchStatsAndUsers(); // Update users list
        } catch (err) {
            const msg = err.response?.data?.error || "Error al cambiar estado";
            alert(msg);
        }
    };

    const handleChangeRole = async (userId, newRole) => {
        if (!window.confirm(`¿Seguro que deseas cambiar el rol a ${newRole}?`)) return;

        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Token ${token}` } };
            await axios.patch(`${API_URL}/api/users/${userId}/change_role/`, { role: newRole }, config);
            fetchStatsAndUsers(); // Update users list
        } catch (err) {
            const msg = err.response?.data?.error || "Error al cambiar rol";
            alert(msg);
        }
    };

    const handleLogout = () => {
        localStorage.clear();
        window.location.href = '/login';
    };

    const username = localStorage.getItem('username') || 'Admin';

    if (loading) return (
        <div className="flex h-screen items-center justify-center bg-background text-white">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-400 animate-pulse">Cargando Panel de Administración...</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="flex h-screen items-center justify-center bg-background text-danger">
            <div className="flex flex-col items-center gap-4 text-center">
                <ShieldAlert className="w-16 h-16 opacity-50" />
                <h2 className="text-2xl font-bold">Error de Acceso</h2>
                <p className="text-gray-400">{error}</p>
                <button onClick={reloadAll} className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white mt-4 transition-colors">
                    Reintentar
                </button>
            </div>
        </div>
    );

    return (
        <div className="flex h-screen bg-background text-white overflow-hidden font-sans">
            {/* Sidebar */}
            <aside className="w-72 bg-surface border-r border-border flex flex-col flex-shrink-0 z-20">
                <div className="p-8 border-b border-border">
                    <div className="flex items-center gap-4">
                        <div className="relative group scroll-py-20">
                            <div className="absolute inset-0 bg-yellow-500/20 rounded-xl blur-lg group-hover:bg-yellow-500/40 transition-all duration-300" />
                            <div className="relative bg-white p-2 rounded-xl shadow-lg border-2 border-white/50 transform transition-transform duration-300 hover:scale-105 hover:rotate-2">
                                <img
                                    src="/assets/logo_tecnicontrol.jpg"
                                    alt="Tecnicontrol Logo"
                                    className="h-12 w-auto object-contain rounded-lg filter drop-shadow-sm"
                                />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-white font-bold text-xl leading-none tracking-tight">Admin<span className="text-yellow-500">SOC</span></h1>
                            <p className="text-gray-500 text-xs font-medium tracking-widest uppercase mt-1">Talleres Luis Mera</p>
                        </div>
                    </div>
                </div>

                <div className="p-6 border-b border-border bg-black/20">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-yellow-500 to-orange-600 p-[2px]">
                            <div className="w-full h-full rounded-full bg-surface flex items-center justify-center">
                                <span className="text-white font-bold text-lg">{username[0].toUpperCase()}</span>
                            </div>
                        </div>
                        <div>
                            <p className="text-white font-bold text-sm">{username}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                <p className="text-yellow-500 text-xs font-bold uppercase tracking-wider">Administrador</p>
                            </div>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 p-6 space-y-2 overflow-y-auto">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Módulos</p>
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all font-medium ${activeTab === 'dashboard'
                            ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20 shadow-lg shadow-blue-900/10'
                            : 'text-gray-400 hover:bg-white/5 hover:text-white'
                            }`}
                    >
                        <LayoutDashboard className="w-5 h-5" />
                        <span>Dashboard General</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all font-medium ${activeTab === 'users'
                            ? 'bg-yellow-600/10 text-yellow-400 border border-yellow-600/20 shadow-lg shadow-yellow-900/10'
                            : 'text-gray-400 hover:bg-white/5 hover:text-white'
                            }`}
                    >
                        <Users className="w-5 h-5" />
                        <span>Usuarios y Accesos</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('audit')}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all font-medium ${activeTab === 'audit'
                            ? 'bg-green-600/10 text-green-400 border border-green-600/20 shadow-lg shadow-green-900/10'
                            : 'text-gray-400 hover:bg-white/5 hover:text-white'
                            }`}
                    >
                        <ShieldAlert className="w-5 h-5" />
                        <span>Auditoría de Seguridad</span>
                    </button>
                </nav>

                <div className="p-6 border-t border-border">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 p-3 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all group"
                    >
                        <LogOut className="w-5 h-5 group-hover:text-danger transition-colors" />
                        <span>Cerrar Sesión</span>
                    </button>
                    <p className="text-center text-gray-600 text-[10px] mt-4 font-mono">v.1.2.0 Admin</p>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
                <header className="bg-surface/50 backdrop-blur-md border-b border-border p-6 flex justify-between items-center sticky top-0 z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                            {activeTab === 'dashboard' && <LayoutDashboard className="w-6 h-6 text-blue-400" />}
                            {activeTab === 'users' && <Users className="w-6 h-6 text-yellow-400" />}
                            {activeTab === 'audit' && <ShieldAlert className="w-6 h-6 text-green-400" />}

                            {activeTab === 'dashboard' && 'Dashboard & Incidentes'}
                            {activeTab === 'users' && 'Gestión de Usuarios'}
                            {activeTab === 'audit' && 'Auditoría de Seguridad'}
                        </h2>
                        <p className="text-gray-400 text-sm mt-1">Panel de control administrativo</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="bg-surface border border-border rounded-lg px-3 py-1.5 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            <span className="text-xs font-bold text-gray-400">SISTEMA SEGURO</span>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8 bg-background scroll-smooth">

                    {activeTab === 'dashboard' && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <div className="mb-8">
                                <StatisticsCards stats={stats} />
                            </div>

                            {/* Filters */}
                            <div className="bg-surface p-1 rounded-xl shadow-lg border border-border mb-8 flex flex-wrap items-center justify-between sticky top-4 z-10 backdrop-blur-xl bg-opacity-80">
                                <div className="flex-1 p-2">
                                    <div className="relative group w-full max-w-md">
                                        <Search className="absolute left-3 top-3 w-5 h-5 text-gray-500 group-focus-within:text-primary transition-colors" />
                                        <input
                                            type="text"
                                            placeholder="Buscar incidentes..."
                                            className="bg-background border border-border text-white pl-10 pr-4 py-2.5 rounded-lg w-full focus:ring-2 focus:ring-primary/50 focus:border-primary/50 outline-none transition-all placeholder-gray-500"
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                        />
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 p-2 border-l border-border pl-4">
                                    <div className="flex items-center gap-2 mr-2">
                                        <Filter className="w-4 h-4 text-gray-500" />
                                        <span className="text-xs font-bold text-gray-500 uppercase">Filtros</span>
                                    </div>
                                    <div className="relative">
                                        <select
                                            className="appearance-none bg-background border border-border text-gray-200 pl-4 pr-10 py-2.5 rounded-lg outline-none focus:border-primary/50 cursor-pointer hover:border-gray-500 transition-colors text-sm font-medium"
                                            value={filterType}
                                            onChange={(e) => setFilterType(e.target.value)}
                                        >
                                            <option value="all">Tipos: Todos</option>
                                            <option value="file">Tipos: Archivos</option>
                                            <option value="url">Tipos: URLs</option>
                                        </select>
                                        <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>
                                    <div className="relative">
                                        <select
                                            className="appearance-none bg-background border border-border text-gray-200 pl-4 pr-10 py-2.5 rounded-lg outline-none focus:border-primary/50 cursor-pointer hover:border-gray-500 transition-colors text-sm font-medium"
                                            value={filterRisk}
                                            onChange={(e) => setFilterRisk(e.target.value)}
                                        >
                                            <option value="">Riesgo: Todos</option>
                                            <option value="CRITICAL">Crítico (Rojo)</option>
                                            <option value="HIGH">Alto (Naranja)</option>
                                            <option value="MEDIUM">Medio (Amarillo)</option>
                                            <option value="LOW">Bajo (Azul)</option>
                                        </select>
                                        <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>
                                </div>
                            </div>

                            <IncidentsTable
                                incidents={filteredIncidents}
                                onView={(incident) => { setSelectedIncident(incident); setShowDetailModal(true); }}
                                onChangeState={(incident) => { setIncidentToChange(incident); setShowChangeStateModal(true); }}
                            />
                        </motion.div>
                    )}

                    {activeTab === 'users' && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <UsersTable
                                users={users}
                                onToggleStatus={handleToggleStatus}
                                onChangeRole={handleChangeRole}
                            />
                        </motion.div>
                    )}

                    {activeTab === 'audit' && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <LoginAttemptsTable attempts={loginAttempts} />
                        </motion.div>
                    )}

                </main>
            </div>

            {/* Modals */}
            {showDetailModal && selectedIncident && (
                <IncidentDetailModal
                    incident={selectedIncident}
                    onClose={() => setShowDetailModal(false)}
                    onUpdate={reloadAll}
                />
            )}

            {showChangeStateModal && incidentToChange && (
                <ChangeStateModal
                    incident={incidentToChange}
                    onClose={() => setShowChangeStateModal(false)}
                    onUpdate={reloadAll}
                />
            )}
        </div>
    );
};

export default AdminDashboard;
