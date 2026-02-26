import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, ChevronLeft, ChevronRight, Activity } from 'lucide-react';

const ITEMS_PER_PAGE = 20;

const LoginAttemptsTable = ({ attempts }) => {
    const [currentPage, setCurrentPage] = useState(1);

    // Paginacion
    const totalPages = Math.ceil(attempts.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const paginatedAttempts = attempts.slice(startIndex, endIndex);

    // Reset a pagina 1 cuando cambian los logs
    React.useEffect(() => {
        setCurrentPage(1);
    }, [attempts.length]);

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
                        <th className="px-6 py-4">Fecha y Hora</th>
                        <th className="px-6 py-4">Usuario</th>
                        <th className="px-6 py-4">Dirección IP</th>
                        <th className="px-6 py-4">Dispositivo / Navegador</th>
                        <th className="px-6 py-4">Estado</th>
                    </tr>
                </thead>
                <motion.tbody
                    className="divide-y divide-border"
                    key={currentPage}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                >
                    {paginatedAttempts.map((attempt) => (
                        <motion.tr
                            key={attempt.id}
                            className="hover:bg-white/5 transition-colors group"
                        >
                            <td className="px-6 py-4 text-gray-300 text-sm">
                                {attempt.timestamp_formatted.split(' ')[0]}
                                <span className="text-gray-500 text-xs block mt-1">
                                    {attempt.timestamp_formatted.split(' ')[1]}
                                </span>
                            </td>
                            <td className="px-6 py-4">
                                <span className="text-white text-sm font-medium">{attempt.username}</span>
                            </td>
                            <td className="px-6 py-4 text-gray-400 font-mono text-sm max-w-xs truncate" title={attempt.ip_address}>
                                {attempt.ip_address || "Detectando..."}
                            </td>
                            <td className="px-6 py-4 text-gray-500 text-xs max-w-sm truncate" title={attempt.user_agent}>
                                {attempt.user_agent || "Desconocido"}
                            </td>
                            <td className="px-6 py-4">
                                {attempt.successful ? (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                                        <ShieldCheck className="w-3.5 h-3.5" /> Exitoso
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                                        <ShieldAlert className="w-3.5 h-3.5" /> Fallido
                                    </span>
                                )}
                            </td>
                        </motion.tr>
                    ))}
                </motion.tbody>
            </table>

            {attempts.length === 0 && (
                <div className="p-12 text-center flex flex-col items-center justify-center text-gray-500">
                    <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                        <Activity className="w-8 h-8 opacity-50" />
                    </div>
                    <p className="text-lg font-medium text-gray-400">Sin registros</p>
                    <p className="text-sm">No existen intentos de sesión almacenados.</p>
                </div>
            )}

            {/* Paginacion */}
            {attempts.length > 0 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-background/30">
                    <div className="text-sm text-gray-500">
                        Página <span className="text-gray-300 font-medium">{currentPage}</span> de <span className="text-gray-300 font-medium">{totalPages}</span>
                        <span className="mx-2 text-gray-600">·</span>
                        <span className="text-gray-300 font-medium">{attempts.length}</span> registros totales
                    </div>
                    {totalPages > 1 && (
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
                    )}
                </div>
            )}
        </div>
    );
};

export default LoginAttemptsTable;
