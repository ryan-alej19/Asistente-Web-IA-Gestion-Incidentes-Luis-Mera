import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { Icons } from '../components/Icons'; // Asegúrate de tener este componente

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const AnalystDashboard = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [stats, setStats] = useState(null);
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(false);

    // Datos para la paginacion
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [nextPage, setNextPage] = useState(null);
    const [prevPage, setPrevPage] = useState(null);

    // Filtros de busqueda
    const [filterRisk, setFilterRisk] = useState('');
    const [filterStatus, setFilterStatus] = useState('');
    const [filterDateFrom, setFilterDateFrom] = useState('');
    const [filterDateTo, setFilterDateTo] = useState('');

    const [selectedIncident, setSelectedIncident] = useState(null);
    const [analystNotes, setAnalystNotes] = useState(''); // Estado para notas

    useEffect(() => {
        if (activeTab === 'dashboard') {
            fetchStats();
        } else if (activeTab === 'incidents') {
            fetchIncidents();
        }
    }, [activeTab, currentPage, filterRisk, filterStatus, filterDateFrom, filterDateTo]);

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('http://localhost:8000/api/incidents/stats/', {
                headers: { Authorization: `Token ${token}` }
            });
            setStats(res.data);
        } catch (err) {
            console.error("Error fetching stats:", err);
        }
    };

    const fetchIncidents = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            let url = `http://localhost:8000/api/incidents/list/?page=${currentPage}`;
            if (filterRisk) url += `&risk_level=${filterRisk}`;
            if (filterStatus) url += `&status=${filterStatus}`;
            if (filterDateFrom) url += `&date_from=${filterDateFrom}`;
            if (filterDateTo) url += `&date_to=${filterDateTo}`;

            const res = await axios.get(url, {
                headers: { Authorization: `Token ${token}` }
            });

            setIncidents(res.data.results);
            setTotalPages(Math.ceil(res.data.count / 10)); // Total divideo por 10 items por pagina
            setNextPage(res.data.next);
            setPrevPage(res.data.previous);
        } catch (err) {
            console.error("Error fetching incidents:", err);
        } finally {
            setLoading(false);
        }
    };

    const updateStatus = async (id, newStatus) => {
        try {
            const token = localStorage.getItem('token');
            await axios.patch(`http://localhost:8000/api/incidents/${id}/update-status/`, {
                status: newStatus,
                analyst_notes: analystNotes
            }, {
                headers: { Authorization: `Token ${token}` }
            });
            // Recargar datos
            if (activeTab === 'dashboard') fetchStats();
            if (activeTab === 'incidents') fetchIncidents();

            // Cerrar modal o actualizar estado local
            if (selectedIncident && selectedIncident.id === id) {
                // Actualizo lo que se ve en pantalla rapido
                setSelectedIncident(prev => ({ ...prev, status: newStatus, analyst_notes: analystNotes }));
            }
            alert(`Estado actualizado a: ${newStatus}`);
            setAnalystNotes('');
        } catch (err) {
            console.error(err);
            alert('Error actualizando estado');
        }
    };

    const handleLogout = () => {
        localStorage.clear();
        window.location.href = '/login';
    };

    // Componentes visuales
    const renderSidebar = () => (
        <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white flex flex-col border-r border-slate-800">
            <div className="flex flex-col justify-center px-6 py-4 border-b border-slate-800 bg-slate-900">
                <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-sm font-bold tracking-tight text-white leading-tight">
                        PANEL ANALISTA <br />
                        <span className="text-indigo-400">CIBERSEGURIDAD</span>
                    </h1>
                </div>
            </div>
            <nav className="flex-1 px-3 py-6 space-y-1">
                <button
                    onClick={() => setActiveTab('dashboard')}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'dashboard' ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20' : 'text-slate-400 hover:bg-slate-800'}`}
                >
                    <Icons.Home className="h-5 w-5" /> Dashboard
                </button>
                <button
                    onClick={() => setActiveTab('incidents')}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'incidents' ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20' : 'text-slate-400 hover:bg-slate-800'}`}
                >
                    <Icons.File className="h-5 w-5" /> Incidentes
                </button>
            </nav>
            <div className="p-4 border-t border-slate-800">
                <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 rounded text-sm text-slate-300 hover:text-white">
                    <Icons.Logout className="h-4 w-4" /> Cerrar Sesión
                </button>
            </div>
        </aside>
    );

    const renderDashboard = () => (
        <div className="animate-fade-in p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-800">Dashboard General</h2>
            {stats ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="card bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                        <h4 className="text-slate-500 text-sm font-semibold uppercase">Total</h4>
                        <p className="text-3xl font-bold text-slate-900 mt-2">{stats.total}</p>
                    </div>
                    <div className="card bg-white p-6 rounded-lg shadow-sm border border-yellow-200 bg-yellow-50">
                        <h4 className="text-yellow-700 text-sm font-semibold uppercase">Pendientes</h4>
                        <p className="text-3xl font-bold text-yellow-800 mt-2">{stats.pending}</p>
                    </div>
                    <div className="card bg-white p-6 rounded-lg shadow-sm border border-red-200 bg-red-50">
                        <h4 className="text-red-700 text-sm font-semibold uppercase">Críticos</h4>
                        <p className="text-3xl font-bold text-red-800 mt-2">{stats.critical}</p>
                    </div>
                    <div className="card bg-slate-700 p-6 rounded-lg shadow-sm border border-slate-600">
                        <h4 className="text-white text-lg font-semibold uppercase">Tipos</h4>
                        <p className="text-white text-lg mt-2">
                            Archivos: {stats.by_type.files} | URLs: {stats.by_type.urls}
                        </p>
                    </div>
                    {/* Seccion de Graficos */}
                    <div className="col-span-1 md:col-span-2 lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                        <h4 className="text-lg font-semibold mb-4 text-slate-800">Distribución de Riesgo</h4>
                        <div className="h-64 flex justify-center">
                            <Pie data={{
                                labels: ['Crítico', 'Alto', 'Medio', 'Bajo'],
                                datasets: [{
                                    data: [stats.critical, 0, 0, stats.total - stats.critical], // Datos de prueba
                                    backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e']
                                }]
                            }} options={{ maintainAspectRatio: false }} />
                        </div>
                    </div>
                </div>
            ) : <p>Cargando estadísticas...</p>}
        </div>
    );

    const renderIncidents = () => (
        <div className="animate-fade-in p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-800">Gestión de Incidentes</h2>

            {/* Filtros */}
            <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 mb-6 flex flex-wrap gap-4 items-end">
                <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">Riesgo</label>
                    <select
                        className="form-select text-sm border-slate-300 rounded-md"
                        value={filterRisk} onChange={e => setFilterRisk(e.target.value)}
                    >
                        <option value="">Todos</option>
                        <option value="CRITICAL">Crítico</option>
                        <option value="HIGH">Alto</option>
                        <option value="MEDIUM">Medio</option>
                        <option value="LOW">Bajo</option>
                    </select>
                </div>
                <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">Estado</label>
                    <select
                        className="form-select text-sm border-slate-300 rounded-md"
                        value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                    >
                        <option value="">Todos</option>
                        <option value="pending">Pendiente</option>
                        <option value="investigating">En Investigación</option>
                        <option value="resolved">Resuelto</option>
                        <option value="closed">Cerrado</option>
                    </select>
                </div>
                <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">Desde</label>
                    <input type="date" className="form-input text-sm border-slate-300 rounded-md"
                        value={filterDateFrom} onChange={e => setFilterDateFrom(e.target.value)}
                    />
                </div>
                <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1">Hasta</label>
                    <input type="date" className="form-input text-sm border-slate-300 rounded-md"
                        value={filterDateTo} onChange={e => setFilterDateTo(e.target.value)}
                    />
                </div>
            </div>

            {/* Tabla */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Fecha</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Tipo</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Objetivo</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Riesgo</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Estado</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {loading ? (
                            <tr><td colSpan="7" className="px-6 py-4 text-center">Cargando...</td></tr>
                        ) : incidents.map((idx) => (
                            <tr key={idx.id} className="hover:bg-slate-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">#{idx.id}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{new Date(idx.created_at).toLocaleDateString()}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 uppercase">{idx.incident_type}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 max-w-xs truncate">{idx.url || idx.attached_file}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full risk-${idx.risk_level}`}>
                                        {idx.risk_level}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 capitalize">{idx.status.replace('_', ' ')}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onClick={() => setSelectedIncident(idx)} className="text-indigo-600 hover:text-indigo-900">Ver Detalle</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {/* Paginacion */}
            <div className="flex justify-between items-center mt-4">
                <span className="text-sm text-slate-500">Página {currentPage} de {totalPages}</span>
                <div className="flex gap-2">
                    <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={!prevPage}
                        className="px-3 py-1 border rounded text-sm disabled:opacity-50"
                    >
                        Anterior
                    </button>
                    <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={!nextPage}
                        className="px-3 py-1 border rounded text-sm disabled:opacity-50"
                    >
                        Siguiente
                    </button>
                </div>
            </div>
        </div>
    );

    return (
        <div className="flex min-h-screen bg-slate-50 font-sans">
            {renderSidebar()}
            <main className="flex-1 ml-64">
                {activeTab === 'dashboard' ? renderDashboard() : renderIncidents()}
            </main>

            {/* Modal de Detalle */}
            {selectedIncident && (
                <div className="fixed inset-0 z-[60] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
                    <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setSelectedIncident(null)}></div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
                            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                <div className="sm:flex sm:items-start">
                                    <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                                        <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                            Incidente #{selectedIncident.id}
                                        </h3>
                                        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {/* Columna Izquierda: Info Gral */}
                                            <div>
                                                <h4 className="font-bold text-slate-700 border-b pb-1 mb-2">Información</h4>
                                                <div className="space-y-2 text-sm text-gray-700">
                                                    <p><span className="font-semibold">Tipo:</span> {selectedIncident.incident_type === 'file' ? 'Archivo' : 'URL'}</p>
                                                    <p><span className="font-semibold">Fecha:</span> {new Date(selectedIncident.created_at).toLocaleString('es-EC')}</p>
                                                    <p><span className="font-semibold">Reportado por:</span> {selectedIncident.reported_by_username || 'Sistema'}</p>
                                                    <p><span className="font-semibold">Fuente:</span> {selectedIncident.virustotal_result?.source || selectedIncident.metadefender_result?.source || 'VirusTotal'}</p>
                                                    <div className="bg-slate-100 p-2 rounded break-all mt-2">
                                                        <span className="font-semibold">Objetivo:</span> {selectedIncident.url || selectedIncident.attached_file}
                                                    </div>
                                                </div>

                                                <h4 className="font-bold text-slate-700 border-b pb-1 mb-2 mt-4">Análisis IA (Gemini)</h4>
                                                <div className="bg-indigo-50 p-3 rounded text-sm text-indigo-900">
                                                    {selectedIncident.gemini_analysis || "Análisis no disponible"}
                                                </div>
                                            </div>

                                            {/* Columna Derecha: Resultados Técnicos */}
                                            <div>
                                                <h4 className="font-bold text-slate-700 border-b pb-1 mb-2">Resultados Motores</h4>

                                                {/* VirusTotal */}
                                                <div className="mb-3">
                                                    <p className="font-semibold text-sm">VirusTotal:</p>
                                                    {selectedIncident.virustotal_result ? (
                                                        <div className="text-xs bg-slate-800 text-green-400 p-2 rounded">
                                                            Positivos: {selectedIncident.virustotal_result.positives} / {selectedIncident.virustotal_result.total}
                                                        </div>
                                                    ) : <span className="text-xs text-slate-400">Sin datos</span>}
                                                </div>

                                                {/* MetaDefender */}
                                                <div className="mb-3">
                                                    <p className="font-semibold text-sm">MetaDefender / GSB:</p>
                                                    {selectedIncident.metadefender_result ? (
                                                        <div className="text-xs bg-slate-800 text-blue-400 p-2 rounded">
                                                            {JSON.stringify(selectedIncident.metadefender_result).substring(0, 100)}...
                                                        </div>
                                                    ) : <span className="text-xs text-slate-400">Sin datos extra</span>}
                                                </div>

                                                <h4 className="font-bold text-slate-700 border-b pb-1 mb-2 mt-4">Gestión</h4>
                                                <textarea
                                                    className="w-full border rounded p-2 text-sm mb-2"
                                                    placeholder="Notas del analista..."
                                                    rows="3"
                                                    value={analystNotes}
                                                    onChange={e => setAnalystNotes(e.target.value)}
                                                />
                                                <p className="text-xs text-slate-500 mb-2">Notas guardadas: {selectedIncident.analyst_notes || 'Ninguna'}</p>
                                                <div className="flex flex-wrap gap-2">
                                                    <button onClick={() => updateStatus(selectedIncident.id, 'investigating')} className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700">Investigar</button>
                                                    <button onClick={() => updateStatus(selectedIncident.id, 'resolved')} className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700">Resolver</button>
                                                    <button onClick={() => updateStatus(selectedIncident.id, 'closed')} className="bg-gray-600 text-white px-3 py-1 rounded text-xs hover:bg-gray-700">Cerrar</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                                <button type="button" className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm" onClick={() => setSelectedIncident(null)}>
                                    Cerrar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalystDashboard;
