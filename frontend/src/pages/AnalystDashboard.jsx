import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
    LayoutDashboard, Shield, LogOut, Search, FileText, Link,
    AlertTriangle, Filter, ChevronDown, Download, FileSpreadsheet
} from 'lucide-react';
import StatisticsCards from '../components/analyst/StatisticsCards';
import IncidentsTable from '../components/analyst/IncidentsTable';
import IncidentDetailModal from '../components/analyst/IncidentDetailModal';
import ChangeStateModal from '../components/analyst/ChangeStateModal';
import API_URL from '../config/api';

const AnalystDashboard = () => {
    const [stats, setStats] = useState(null);
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Filters
    const [filterRisk, setFilterRisk] = useState('');
    const [filterType, setFilterType] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');

    // Modal State
    const [selectedIncident, setSelectedIncident] = useState(null);
    const [incidentToChange, setIncidentToChange] = useState(null);
    const [showDetailModal, setShowDetailModal] = useState(false);
    const [showChangeStateModal, setShowChangeStateModal] = useState(false);

    useEffect(() => {
        fetchStats();
        fetchDashboardData();
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []); // Run once on mount

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Token ${token}` } };
            const response = await axios.get(`${API_URL}/api/incidents/stats/`, config);
            setStats(response.data);
        } catch (err) {
            console.error("Error fetching stats:", err);
        }
    };

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const config = {
                headers: { Authorization: `Token ${token}` }
                // Removed server-side params to use client-side filtering
            };

            // 2. Obtener Lista de Incidentes
            const incidentsRes = await axios.get(`${API_URL}/api/incidents/list/`, config);
            setIncidents(incidentsRes.data.results);

        } catch (err) {
            console.error("Error fetching dashboard data:", err);
            setError("Error al cargar datos.");
        } finally {
            setLoading(false);
        }
    };

    // Filter Logic
    const filteredIncidents = incidents.filter(inc => {
        // Search
        // Search
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            const matchesId = inc.id.toString().includes(term);
            const matchesDesc = inc.description?.toLowerCase().includes(term);
            const matchesRisk = inc.risk_level?.toLowerCase().includes(term);
            const matchesType = inc.incident_type?.toLowerCase().includes(term);
            const matchesUrl = inc.url?.toLowerCase().includes(term);
            const matchesFile = inc.attached_file ? inc.attached_file.toString().toLowerCase().includes(term) : false;

            if (!matchesId && !matchesDesc && !matchesRisk && !matchesType && !matchesUrl && !matchesFile) {
                return false;
            }
        }

        // Filtro por Tipo
        if (filterType !== 'all') {
            const type = inc.incident_type?.toLowerCase() || '';
            if (type !== filterType.toLowerCase()) return false;
        }

        // Filtro por Riesgo
        if (filterRisk && inc.risk_level !== filterRisk) return false;

        return true;
    });


    const handleLogout = () => {
        localStorage.clear();
        window.location.href = '/login';
    };

    const handleExportCSV = async () => {
        try {
            const token = localStorage.getItem('token');

            // Construir parámetros de la URL
            const params = new URLSearchParams();
            if (filterType !== 'all') params.append('type', filterType);
            if (filterRisk) params.append('risk_level', filterRisk);
            // Search term not supported by backend export yet, but we can add if needed
            // if (searchTerm) params.append('search', searchTerm);

            const queryString = params.toString();
            const url = `${API_URL}/api/incidents/export/csv/${queryString ? `?${queryString}` : ''}`;

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`, // Ensure Token prefix matches config
                },
            });

            if (!response.ok) {
                throw new Error('Error al exportar CSV');
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `incidentes_talleres_luis_mera_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);
        } catch (error) {
            console.error('Error al exportar CSV:', error);
            alert('Error al exportar datos CSV');
        }
    };

    const handleExportPDFMonthly = async () => {
        try {
            const token = localStorage.getItem('token');

            const response = await fetch(`${API_URL}/api/incidents/report/pdf/monthly/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Error al generar PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `reporte_mensual_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error al generar PDF:', error);
            alert('Error al generar reporte PDF');
        }
    };

    const username = localStorage.getItem('username') || 'Analista';

    if (loading) return (
        <div className="flex h-screen items-center justify-center bg-background text-white">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-400 animate-pulse">Cargando Dashboard...</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="flex h-screen items-center justify-center bg-background text-danger">
            <div className="flex flex-col items-center gap-4 text-center">
                <AlertTriangle className="w-16 h-16 opacity-50" />
                <h2 className="text-2xl font-bold">Error de Conexión</h2>
                <p className="text-gray-400">{error}</p>
                <button onClick={fetchDashboardData} className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white mt-4 transition-colors">
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
                            <div className="absolute inset-0 bg-primary/20 rounded-xl blur-lg group-hover:bg-primary/40 transition-all duration-300" />
                            <div className="relative bg-white p-2 rounded-xl shadow-lg border-2 border-white/50 transform transition-transform duration-300 hover:scale-105 hover:rotate-2">
                                <img
                                    src="/assets/logo_tecnicontrol.jpg"
                                    alt="Tecnicontrol Logo"
                                    className="h-12 w-auto object-contain rounded-lg filter drop-shadow-sm"
                                />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-white font-bold text-xl leading-none tracking-tight flex items-center gap-2">
                                Centro<span className="text-primary">SOC</span>
                                <span className="text-[9px] bg-primary/20 text-primary border border-primary/30 px-1.5 py-0.5 rounded-full font-bold">
                                    v1.3.0
                                </span>
                            </h1>
                            <p className="text-gray-500 text-xs font-medium tracking-widest uppercase mt-1">Talleres Luis Mera</p>
                        </div>
                    </div>
                </div>

                {/* User Info */}
                <div className="p-6 border-b border-border bg-black/20">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-primary to-blue-600 p-[2px]">
                            <div className="w-full h-full rounded-full bg-surface flex items-center justify-center">
                                <span className="text-white font-bold text-lg">{username[0].toUpperCase()}</span>
                            </div>
                        </div>
                        <div>
                            <p className="text-white font-bold text-sm">{username}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                <p className="text-gray-400 text-xs">En línea</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-6 space-y-2 overflow-y-auto">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Principal</p>
                    <button className="w-full flex items-center gap-3 p-3 rounded-xl bg-primary/10 text-primary border border-primary/20 font-medium transition-all shadow-lg shadow-primary/5">
                        <LayoutDashboard className="w-5 h-5" />
                        <span>Vista General</span>
                    </button>
                    {/* Add more links here if needed */}
                </nav>

                {/* Logout */}
                <div className="p-6 border-t border-border">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 p-3 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all group"
                    >
                        <LogOut className="w-5 h-5 group-hover:text-danger transition-colors" />
                        <span>Cerrar Sesión</span>
                    </button>
                    <p className="text-center text-gray-600 text-[10px] mt-4 font-mono">v.1.2.0</p>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-screen overflow-hidden relative">

                {/* Topbar */}
                <header className="bg-surface/50 backdrop-blur-md border-b border-border p-6 flex justify-between items-center sticky top-0 z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-white">Vista General de Incidentes</h2>
                        <p className="text-gray-400 text-sm">{new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="bg-surface border border-border rounded-lg px-3 py-1.5 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                            <span className="text-xs font-bold text-gray-400">SISTEMA OPERATIVO</span>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8 bg-background scroll-smooth">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        {/* Statistics */}
                        <StatisticsCards stats={stats} />

                        {/* Filters & Toolbar */}
                        <div className="bg-surface p-1 rounded-xl shadow-lg border border-border mb-8 flex flex-wrap items-center justify-between sticky top-4 z-10 backdrop-blur-xl bg-opacity-80">
                            <div className="flex-1 p-2">
                                <div className="relative group w-full max-w-md">
                                    <Search className="absolute left-3 top-3 w-5 h-5 text-gray-500 group-focus-within:text-primary transition-colors" />
                                    <input
                                        type="text"
                                        placeholder="Buscar por ID, usuario..."
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

                            <div className="flex items-center gap-2 p-2 px-4">
                                <button
                                    onClick={handleExportCSV}
                                    className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium shadow-lg shadow-green-600/20"
                                    title="Descargar CSV con filtros actuales"
                                >
                                    <FileSpreadsheet className="h-4 w-4" />
                                    <span>CSV</span>
                                </button>
                                <button
                                    onClick={handleExportPDFMonthly}
                                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium shadow-lg shadow-red-600/20"
                                    title="Descargar Reporte Mensual PDF"
                                >
                                    <FileText className="h-4 w-4" />
                                    <span>PDF Mensual</span>
                                </button>
                            </div>
                        </div>

                        {/* Table */}
                        <IncidentsTable
                            incidents={filteredIncidents}
                            onView={(incident) => { setSelectedIncident(incident); setShowDetailModal(true); }}
                            onChangeState={(incident) => { setIncidentToChange(incident); setShowChangeStateModal(true); }}
                        />
                    </motion.div>
                </main>
            </div>

            {/* Modals placed at root level but conditionally rendered */}
            {showDetailModal && selectedIncident && (
                <IncidentDetailModal
                    incident={selectedIncident}
                    onClose={() => setShowDetailModal(false)}
                    onUpdate={fetchDashboardData}
                />
            )}

            {showChangeStateModal && incidentToChange && (
                <ChangeStateModal
                    incident={incidentToChange}
                    onClose={() => setShowChangeStateModal(false)}
                    onUpdate={fetchDashboardData}
                />
            )}
        </div>
    );
};

export default AnalystDashboard;
