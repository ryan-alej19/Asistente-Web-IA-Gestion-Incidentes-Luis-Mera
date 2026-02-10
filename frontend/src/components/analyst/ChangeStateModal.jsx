import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertTriangle, RefreshCw, Loader2 } from 'lucide-react';

const ChangeStateModal = ({ incident, onClose, onUpdate }) => {
    const [status, setStatus] = useState(incident.status);
    const [note, setNote] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async () => {
        if (status === incident.status) {
            onClose();
            return;
        }

        // Validación: Nota obligatoria para resolver
        if (status === 'resolved' && !note.trim()) {
            setError('Es obligatorio agregar una nota de resolución.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            await axios.patch(`http://localhost:8000/api/incidents/${incident.id}/update-status/`,
                { status: status, analyst_notes: note },
                { headers: { Authorization: `Token ${token}` } }
            );
            onUpdate(); // Recargar tabla
            onClose();
        } catch (err) {
            console.error("Error updating status:", err);
            setError("Error al actualizar estado. Intente nuevamente.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-background/80 backdrop-blur-sm"
                />

                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="bg-surface w-full max-w-md rounded-xl shadow-2xl border border-border p-6 z-10"
                >
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <RefreshCw className="w-5 h-5 text-primary" />
                                Cambiar Estado
                            </h2>
                            <p className="text-sm text-gray-400">Incidente #{incident.id}</p>
                        </div>
                        <button onClick={onClose} className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div className="bg-background/50 p-3 rounded-lg border border-border flex justify-between items-center">
                            <span className="text-sm text-gray-400">Estado Actual:</span>
                            <span className="text-sm font-bold text-primary capitalize px-2 py-1 bg-primary/10 rounded border border-primary/20">
                                {incident.status === 'pending' && 'Pendiente'}
                                {incident.status === 'investigating' && 'Revisión'}
                                {incident.status === 'resolved' && 'Resuelto'}
                                {incident.status === 'closed' && 'Cerrado'}
                            </span>
                        </div>

                        <div>
                            <label className="block text-gray-300 text-sm font-medium mb-2">Nuevo Estado</label>
                            <select
                                className="w-full bg-background text-white border border-border rounded-lg p-3 focus:ring-2 focus:ring-primary outline-none transition-all appearance-none cursor-pointer hover:border-primary/50"
                                value={status}
                                onChange={(e) => setStatus(e.target.value)}
                            >
                                <option value="pending" disabled={incident.status !== 'pending'}>Pendiente</option>
                                <option value="investigating" disabled={incident.status === 'resolved'}>En Revisión</option>
                                <option value="resolved">Resuelto</option>
                                <option value="closed" disabled>Cerrado (Archivado)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-gray-300 text-sm font-medium mb-2">
                                Nota de Cambio
                                {status === 'resolved' && <span className="text-danger ml-1">*</span>}
                            </label>
                            <textarea
                                className={`w-full bg-background text-white border rounded-lg p-3 h-24 focus:ring-2 outline-none transition-all resize-none ${error ? 'border-danger focus:ring-danger' : 'border-border focus:ring-primary'}`}
                                placeholder="Explique la razón del cambio de estado..."
                                value={note}
                                onChange={(e) => setNote(e.target.value)}
                            ></textarea>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="flex items-center gap-2 mt-2 text-danger text-xs font-medium"
                                >
                                    <AlertTriangle className="w-3 h-3" />
                                    {error}
                                </motion.div>
                            )}
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-border">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors text-sm font-medium"
                            disabled={loading}
                        >
                            Cancelar
                        </button>
                        <button
                            onClick={handleSubmit}
                            className="px-4 py-2 rounded-lg bg-primary hover:bg-blue-600 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-primary/20"
                            disabled={loading}
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                            {loading ? 'Guardando...' : 'Confirmar Cambio'}
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default ChangeStateModal;
