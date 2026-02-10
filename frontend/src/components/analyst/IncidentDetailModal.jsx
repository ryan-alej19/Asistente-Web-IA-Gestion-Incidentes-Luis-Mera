import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X, FileText, Link, ShieldAlert, Activity, CheckCircle,
    MessageSquare, Clock, AlertTriangle, User, Calendar,
    ShieldCheck, AlertOctagon, Info, AlertCircle, Download
} from 'lucide-react';
import { GeminiLogo } from '../BrandLogos';

const IncidentDetailModal = ({ incident, onClose, onUpdate }) => {
    const [activeTab, setActiveTab] = useState('info');
    const [notes, setNotes] = useState([]);
    const [newNote, setNewNote] = useState('');
    const [loadingNotes, setLoadingNotes] = useState(false);
    const [analysisDetails, setAnalysisDetails] = useState(null);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);

    useEffect(() => {
        if (activeTab === 'notes' && incident) fetchNotes();
        if (activeTab === 'analysis' && incident) fetchAnalysisDetails();
    }, [activeTab, incident]);

    const handleDownloadReport = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://localhost:8000/api/incidents/${incident.id}/pdf/`, {
                headers: { Authorization: `Token ${token}` },
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `reporte_incidente_${incident.id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Error downloading report:", err);
            alert("Error al descargar reporte. Verifique permisos.");
        }
    };

    const fetchNotes = async () => {
        setLoadingNotes(true);
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`http://localhost:8000/api/incidents/${incident.id}/notes/`, {
                headers: { Authorization: `Token ${token}` }
            });
            setNotes(res.data);
        } catch (err) {
            console.error("Error fetching notes:", err);
        } finally {
            setLoadingNotes(false);
        }
    };

    const fetchAnalysisDetails = async () => {
        setLoadingAnalysis(true);
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`http://localhost:8000/api/incidents/${incident.id}/analysis-details/`, {
                headers: { Authorization: `Token ${token}` }
            });
            setAnalysisDetails(res.data);
        } catch (err) {
            console.error("Error fetching analysis:", err);
        } finally {
            setLoadingAnalysis(false);
        }
    };

    const handleAddNote = async () => {
        if (!newNote.trim()) return;
        try {
            const token = localStorage.getItem('token');
            await axios.post(`http://localhost:8000/api/incidents/${incident.id}/notes/`,
                { content: newNote },
                { headers: { Authorization: `Token ${token}` } }
            );
            setNewNote('');
            fetchNotes();
        } catch (err) {
            console.error("Error adding note:", err);
            alert("Error al guardar la nota");
        }
    };

    if (!incident) return null;

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
                    initial={{ scale: 0.95, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 20 }}
                    className="bg-surface w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl border border-border flex flex-col z-10 overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-border flex justify-between items-center bg-surface">
                        <div className="flex items-center gap-4">
                            <div className={`p-3 rounded-xl border ${incident.incident_type === 'file' ? 'bg-purple-500/10 border-purple-500/20 text-purple-400' : 'bg-blue-500/10 border-blue-500/20 text-blue-400'}`}>
                                {incident.incident_type === 'file' ? <FileText className="w-6 h-6" /> : <Link className="w-6 h-6" />}
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                    Incidente #{incident.id}
                                    <span className="text-sm font-normal text-gray-400 px-2 py-0.5 rounded-full border border-border bg-background">
                                        v1.0
                                    </span>
                                </h2>
                                <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
                                    <div className="flex items-center gap-1">
                                        <Calendar className="w-3 h-3" />
                                        {new Date(incident.created_at).toLocaleString()}
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <User className="w-3 h-3" />
                                        Reportado por <span className="text-white font-medium">{incident.reported_by_username}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={handleDownloadReport}
                                className="flex items-center gap-2 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 px-4 py-2 rounded-lg transition-colors font-medium text-sm"
                            >
                                <Download className="w-4 h-4" />
                                Reporte PDF
                            </button>
                            <button onClick={onClose} className="text-gray-400 hover:text-white hover:bg-white/5 p-2 rounded-lg transition-colors">
                                <X className="w-6 h-6" />
                            </button>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="flex px-6 border-b border-border bg-surface/50 gap-8">
                        {[
                            { id: 'info', label: 'Información General', icon: Info },
                            { id: 'analysis', label: 'Análisis Técnico', icon: Activity },
                            { id: 'notes', label: `Notas Internas (${notes.length})`, icon: MessageSquare }
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === tab.id
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
                                    }`}
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Content Area */}
                    <div className="p-6 overflow-y-auto bg-background/50 flex-1">

                        {/* TAB: INFO */}
                        {activeTab === 'info' && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="space-y-6"
                            >
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="bg-surface p-5 rounded-xl border border-border">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 block">Estado Actual</label>
                                        <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-bold border ${incident.status === 'pending' ? 'bg-gray-500/10 text-gray-300 border-gray-500/20' :
                                            incident.status === 'investigating' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                                'bg-green-500/10 text-green-400 border-green-500/20'
                                            }`}>
                                            {incident.status === 'pending' && <Clock className="w-4 h-4 mr-2" />}
                                            {incident.status === 'investigating' && <Activity className="w-4 h-4 mr-2" />}
                                            {incident.status === 'resolved' && <CheckCircle className="w-4 h-4 mr-2" />}

                                            {incident.status === 'pending' && 'PENDIENTE'}
                                            {incident.status === 'investigating' && 'EN REVISIÓN'}
                                            {incident.status === 'resolved' && 'RESUELTO'}
                                        </span>
                                    </div>
                                    <div className="bg-surface p-5 rounded-xl border border-border">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 block">Nivel de Riesgo</label>
                                        <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-bold border ${incident.risk_level === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                            incident.risk_level === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                                                incident.risk_level === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                                    incident.risk_level === 'LOW' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                                        'bg-green-500/10 text-green-400 border-green-500/20'
                                            }`}>
                                            {incident.risk_level === 'CRITICAL' && <ShieldAlert className="w-4 h-4 mr-2" />}
                                            {incident.risk_level === 'HIGH' && <AlertTriangle className="w-4 h-4 mr-2" />}
                                            {incident.risk_level === 'MEDIUM' && <AlertCircle className="w-4 h-4 mr-2" />}
                                            {incident.risk_level === 'LOW' && <ShieldCheck className="w-4 h-4 mr-2" />}
                                            {incident.risk_level === 'SAFE' && <CheckCircle className="w-4 h-4 mr-2" />}

                                            {incident.risk_level === 'CRITICAL' && 'CRÍTICO'}
                                            {incident.risk_level === 'HIGH' && 'ALTO'}
                                            {incident.risk_level === 'MEDIUM' && 'MEDIO'}
                                            {incident.risk_level === 'LOW' && 'BAJO'}
                                            {incident.risk_level === 'SAFE' && 'SEGURO'}
                                        </span>
                                    </div>
                                </div>

                                <div className="bg-surface p-6 rounded-xl border border-border">
                                    <label className="text-xs font-bold text-primary uppercase tracking-wider mb-3 block">Objetivo Analizado</label>
                                    <div className="flex items-center bg-background p-4 rounded-lg border border-border font-mono text-gray-200 text-sm break-all">
                                        {incident.incident_type === 'url' ? incident.url : (incident.attached_file ? incident.attached_file.split('/').pop() : 'Archivo adjunto')}
                                    </div>
                                </div>

                                <div className="bg-surface p-6 rounded-xl border border-border">
                                    <label className="text-xs font-bold text-primary uppercase tracking-wider mb-3 block">Descripción del Usuario</label>
                                    <p className="text-gray-300 leading-relaxed italic border-l-2 border-border pl-4">
                                        "{incident.description || 'Sin descripción'}"
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {/* TAB: ANALYSIS */}
                        {activeTab === 'analysis' && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="space-y-6"
                            >
                                {loadingAnalysis ? (
                                    <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                                        <Activity className="w-10 h-10 animate-spin text-primary mb-4" />
                                        <p>Conectando con servicios de inteligencia...</p>
                                    </div>
                                ) : analysisDetails ? (
                                    <>
                                        {/* Gemini */}
                                        <div className="bg-surface rounded-xl border border-border overflow-hidden">
                                            <div className="bg-gradient-to-r from-blue-900/10 to-purple-900/10 p-4 border-b border-border flex items-center gap-3">
                                                <GeminiLogo className="w-6 h-6" />
                                                <h3 className="text-white font-bold">Análisis Inteligente (Gemini AI)</h3>
                                            </div>
                                            <div className="p-6">
                                                <div className="mb-6">
                                                    <h4 className="text-xs font-bold text-primary uppercase tracking-wider mb-3">Explicación de la Amenaza</h4>
                                                    <div className="text-gray-300 leading-relaxed text-sm whitespace-pre-wrap pl-4 border-l-2 border-primary/30">
                                                        {analysisDetails.gemini_explicacion || "Análisis no disponible."}
                                                    </div>
                                                </div>
                                                {analysisDetails.gemini_recomendacion && (
                                                    <div className="bg-blue-500/5 p-4 rounded-lg border border-blue-500/10">
                                                        <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">Recomendación de Seguridad</h4>
                                                        <p className="text-white text-sm font-medium">{analysisDetails.gemini_recomendacion}</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Engines */}
                                        <div className="bg-surface rounded-xl border border-border p-6">
                                            <div className="flex items-center justify-between mb-6">
                                                <h3 className="text-white font-bold flex items-center gap-2">
                                                    <ShieldCheck className="w-5 h-5 text-primary" />
                                                    Motores de Seguridad
                                                </h3>
                                                <span className="text-xs text-gray-500 font-bold bg-white/5 px-2 py-1 rounded">
                                                    Resultados en Tiempo Real
                                                </span>
                                            </div>

                                            {analysisDetails.engines && analysisDetails.engines.length > 0 ? (
                                                <div className="space-y-3">
                                                    {analysisDetails.engines.map((engine, idx) => (
                                                        <motion.div
                                                            key={idx}
                                                            initial={{ opacity: 0, x: -10 }}
                                                            animate={{ opacity: 1, x: 0 }}
                                                            transition={{ delay: idx * 0.05 }}
                                                            className="bg-background p-4 rounded-lg border border-border flex justify-between items-center hover:border-border/80 transition-colors"
                                                        >
                                                            <div className="flex items-center gap-3">
                                                                <div className={`p-2 rounded-lg ${engine.positives > 0 ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                                                                    {engine.positives > 0 ? <AlertOctagon className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                                                                </div>
                                                                <div>
                                                                    <h4 className="text-white font-bold text-sm">{engine.name}</h4>
                                                                    <p className="text-xs text-gray-500">{engine.status_text || 'Análisis completado'}</p>
                                                                </div>
                                                            </div>
                                                            <div className="text-right">
                                                                {engine.positives !== undefined ? (
                                                                    <div className={`text-xs font-mono font-bold px-2 py-1 rounded ${engine.positives > 0 ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'}`}>
                                                                        {engine.positives} / {engine.total}
                                                                    </div>
                                                                ) : (
                                                                    <div className={`text-xs font-bold px-2 py-1 rounded ${engine.alert ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'}`}>
                                                                        {engine.alert ? 'DETECTADO' : 'LIMPIO'}
                                                                    </div>
                                                                )}
                                                                {engine.link && engine.link !== '#' && (
                                                                    <a href={engine.link} target="_blank" rel="noreferrer" className="text-primary hover:text-white text-xs mt-1 block transition-colors">
                                                                        Ver Reporte
                                                                    </a>
                                                                )}
                                                            </div>
                                                        </motion.div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-8 text-gray-500 border border-dashed border-gray-700 rounded-lg">
                                                    Sin datos de motores disponibles
                                                </div>
                                            )}
                                        </div>
                                    </>
                                ) : (
                                    <div className="p-8 text-center bg-red-500/10 border border-red-500/20 rounded-xl">
                                        <p className="text-red-400 font-bold">Error al cargar datos</p>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {/* TAB: NOTES */}
                        {activeTab === 'notes' && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex flex-col h-full"
                            >
                                <div className="flex-1 overflow-y-auto pr-2 space-y-4 mb-4 custom-scrollbar max-h-[400px]">
                                    {loadingNotes ? (
                                        <div className="text-center py-8 text-gray-500"><Activity className="w-6 h-6 animate-spin mx-auto mb-2" />Cargando notas...</div>
                                    ) : notes.length === 0 ? (
                                        <div className="text-center py-12 border border-dashed border-border rounded-xl">
                                            <MessageSquare className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                                            <p className="text-gray-400 mb-1">No hay notas registradas</p>
                                            <p className="text-gray-500 text-xs">Agrega una nota para iniciar el historial.</p>
                                        </div>
                                    ) : (
                                        notes.map((note, idx) => (
                                            <div key={note.id} className="bg-surface p-4 rounded-xl border border-border">
                                                <div className="flex justify-between items-center mb-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold uppercase">
                                                            {note.author_username.charAt(0)}
                                                        </div>
                                                        <span className="text-primary font-bold text-sm">{note.author_username}</span>
                                                    </div>
                                                    <span className="text-gray-500 text-xs font-mono">{new Date(note.created_at).toLocaleString()}</span>
                                                </div>
                                                <p className="text-gray-300 text-sm leading-relaxed pl-8 border-l-2 border-border">
                                                    {note.content}
                                                </p>
                                            </div>
                                        ))
                                    )}
                                </div>
                                <div className="bg-surface p-4 rounded-xl border border-border">
                                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Nueva Nota</label>
                                    <textarea
                                        className="w-full bg-background text-white rounded-lg p-3 text-sm border border-border focus:ring-1 focus:ring-primary outline-none transition-all resize-none"
                                        rows="3"
                                        placeholder="Escriba detalles, observaciones o acciones tomadas..."
                                        value={newNote}
                                        onChange={(e) => setNewNote(e.target.value)}
                                    />
                                    <div className="flex justify-end mt-3">
                                        <button
                                            className="bg-primary hover:bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
                                            onClick={handleAddNote}
                                            disabled={!newNote.trim()}
                                        >
                                            Guardar Nota
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default IncidentDetailModal;
