import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
    FileText, Link, ShieldAlert, ShieldCheck, AlertTriangle, AlertCircle,
    CheckCircle, Eye, RefreshCw, HelpCircle, ChevronLeft, ChevronRight
} from 'lucide-react';

const ITEMS_PER_PAGE = 20;

const IncidentsTable = ({ incidents, onView, onChangeState }) => {

    const [currentPage, setCurrentPage] = useState(1);

    // Paginacion
    const totalPages = Math.ceil(incidents.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const paginatedIncidents = incidents.slice(startIndex, endIndex);

    // Reset a pagina 1 cuando cambian los filtros
    React.useEffect(() => {
        setCurrentPage(1);
    }, [incidents.length]);

    // Generar numeros de pagina visibles
    const getPageNumbers = () => {
        const pages = [];
        const maxVisible = 5;
        let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);
        if (end - start < maxVisible - 1) {
            start = Math.max(1, end - maxVisible + 1);
        }
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        return pages;
    };

    return (
        <div className="bg-surface rounded-xl border border-border overflow-hidden shadow-lg">
            <table className="w-full text-left">
                <thead className="bg-background/50 text-gray-400 uppercase text-xs font-bold tracking-wider border-b border-border">
                    <tr>
                        <th className="px-6 py-4">ID</th>
                        <th className="px-6 py-4">Fecha</th>
                        <th className="px-6 py-4">Reportado Por</th>
                        <th className="px-6 py-4">Tipo</th>
                        <th className="px-6 py-4">Riesgo</th>
                        <th className="px-6 py-4">Estado</th>
                        <th className="px-6 py-4 text-right">Acciones</th>
                    </tr>
                </thead>
                <motion.tbody
                    className="divide-y divide-border"
                    key={currentPage}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                >
                    {paginatedIncidents.map((incident) => (
                        <motion.tr
                            key={incident.id}
                            className="hover:bg-white/5 transition-colors group"
                        >
                            <td className="px-6 py-4 text-gray-500 font-mono text-sm">#{incident.id}</td>
                            <td className="px-6 py-4 text-gray-300 text-sm">
                                {new Date(incident.created_at).toLocaleDateString()}
                                <span className="text-gray-500 text-xs block mt-1">
                                    {new Date(incident.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center">
                                    <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xs mr-3 border border-primary/30">
                                        {incident.reported_by_username ? incident.reported_by_username[0].toUpperCase() : '?'}
                                    </div>
                                    <span className="text-white text-sm font-medium">{incident.reported_by_username}</span>
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                {incident.incident_type === 'file' ? (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                        <FileText className="w-3 h-3" /> Archivo
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
                                        <Link className="w-3 h-3" /> URL
                                    </span>
                                )}
                            </td>
                            <td className="px-6 py-4">
                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border
                                    ${incident.risk_level === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                        incident.risk_level === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                                            incident.risk_level === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                                incident.risk_level === 'LOW' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                                    'bg-green-500/10 text-green-400 border-green-500/20'}`}>

                                    {incident.risk_level === 'CRITICAL' && <ShieldAlert className="w-3.5 h-3.5" />}
                                    {incident.risk_level === 'HIGH' && <AlertTriangle className="w-3.5 h-3.5" />}
                                    {incident.risk_level === 'MEDIUM' && <AlertCircle className="w-3.5 h-3.5" />}
                                    {incident.risk_level === 'LOW' && <ShieldCheck className="w-3.5 h-3.5" />}
                                    {incident.risk_level === 'SAFE' && <CheckCircle className="w-3.5 h-3.5" />}
                                    {incident.risk_level === 'UNKNOWN' && <HelpCircle className="w-3.5 h-3.5" />}

                                    {incident.risk_level === 'CRITICAL' && 'CRÍTICO'}
                                    {incident.risk_level === 'HIGH' && 'ALTO'}
                                    {incident.risk_level === 'MEDIUM' && 'MEDIO'}
                                    {incident.risk_level === 'LOW' && 'BAJO'}
                                    {incident.risk_level === 'SAFE' && 'SEGURO'}
                                    {incident.risk_level === 'UNKNOWN' && 'DESC.'}
                                </span>
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center gap-2">
                                    <span className={`w-2 h-2 rounded-full ${incident.status === 'pending' ? 'bg-gray-500 animate-pulse' :
                                        incident.status === 'investigating' ? 'bg-yellow-500 animate-pulse' :
                                            'bg-green-500'
                                        }`}></span>
                                    <span className={`text-xs font-medium ${incident.status === 'pending' ? 'text-gray-400' :
                                        incident.status === 'investigating' ? 'text-yellow-400' :
                                            'text-green-400'
                                        }`}>
                                        {incident.status === 'pending' && 'Pendiente'}
                                        {incident.status === 'investigating' && 'Revisión'}
                                        {incident.status === 'resolved' && 'Resuelto'}
                                        {incident.status === 'closed' && 'Cerrado'}
                                    </span>
                                </div>
                            </td>
                            <td className="px-6 py-4 text-right">
                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        className="text-gray-400 hover:text-white transition-colors bg-white/5 hover:bg-white/10 p-2 rounded-lg"
                                        title="Ver detalles"
                                        onClick={() => onView(incident)}
                                    >
                                        <Eye className="w-4 h-4" />
                                    </button>
                                    <button
                                        className="text-primary hover:text-white transition-colors bg-primary/10 hover:bg-primary p-2 rounded-lg"
                                        title="Gestionar estado"
                                        onClick={() => onChangeState(incident)}
                                    >
                                        <RefreshCw className="w-4 h-4" />
                                    </button>
                                </div>
                            </td>
                        </motion.tr>
                    ))}
                </motion.tbody>
            </table>

            {incidents.length === 0 && (
                <div className="p-12 text-center flex flex-col items-center justify-center text-gray-500">
                    <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                        <FileText className="w-8 h-8 opacity-50" />
                    </div>
                    <p className="text-lg font-medium text-gray-400">Sin incidentes</p>
                    <p className="text-sm">No hay incidentes que coincidan con los filtros.</p>
                </div>
            )}

            {/* Paginacion */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-background/30">
                    <div className="text-sm text-gray-500">
                        Mostrando <span className="text-gray-300 font-medium">{startIndex + 1}</span> - <span className="text-gray-300 font-medium">{Math.min(endIndex, incidents.length)}</span> de <span className="text-gray-300 font-medium">{incidents.length}</span> incidentes
                    </div>
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </button>

                        {getPageNumbers().map(page => (
                            <button
                                key={page}
                                onClick={() => setCurrentPage(page)}
                                className={`min-w-[36px] h-9 rounded-lg text-sm font-medium transition-all ${currentPage === page
                                        ? 'bg-primary text-white shadow-lg shadow-primary/30'
                                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                                    }`}
                            >
                                {page}
                            </button>
                        ))}

                        <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default IncidentsTable;
