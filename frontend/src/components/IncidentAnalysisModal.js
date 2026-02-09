import React, { useState } from 'react';
import { Icons } from './Icons';
import { updateIncidentStatus } from '../services/api';

/**
 * Modal para que el analista revise el incidente, vea el análisis de la IA
 * y tome acciones (cambiar estado, añadir notas).
 */
function IncidentAnalysisModal({ incident, onClose, onUpdate }) {
  const [status, setStatus] = useState(incident.status);
  const [notes, setNotes] = useState(incident.analyst_notes || '');
  const [updating, setUpdating] = useState(false);

  if (!incident) return null;

  const handleUpdate = async () => {
    try {
      setUpdating(true);
      await updateIncidentStatus(incident.id, {
        status: status,
        analyst_notes: notes
      });

      // Notificar al padre para recargar la lista
      if (onUpdate) onUpdate();
      onClose(); // Cerrar modal

    } catch (error) {
      console.error("Error updating incident:", error);
      alert("Error al actualizar el incidente (ver consola)");
    } finally {
      setUpdating(false);
    }
  };

  // Parsers seguros para JSON
  const getGeminiAnalysis = () => {
    if (!incident.gemini_analysis) return null;
    return typeof incident.gemini_analysis === 'string'
      ? JSON.parse(incident.gemini_analysis)
      : incident.gemini_analysis;
  };

  const getVirusTotal = () => {
    if (!incident.virustotal_result) return null;
    return typeof incident.virustotal_result === 'string'
      ? JSON.parse(incident.virustotal_result)
      : incident.virustotal_result;
  };

  const gemini = getGeminiAnalysis();
  const vt = getVirusTotal();

  const getSeverityColor = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'crítico': case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'alto': case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medio': case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 animate-fade-in backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">

        {/* ENCABEZADO */}
        <div className="p-6 border-b border-slate-100 flex justify-between items-start bg-slate-50">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="font-mono text-sm font-bold text-slate-500">#{incident.id}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase border ${getSeverityColor(incident.risk_level || incident.severity)}`}>
                {incident.risk_level || incident.severity}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-800">{incident.incident_type}</h2>
            <p className="text-sm text-slate-500">Reportado por: {incident.reported_by_username} • {new Date(incident.created_at).toLocaleString()}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-full hover:bg-slate-200">
            <Icons.X className="h-6 w-6" />
          </button>
        </div>

        {/* CONTENIDO - CON SCROLL */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* 1. DESCRIPCIÓN */}
          <section>
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Descripción del Reporte</h3>
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 text-slate-700 leading-relaxed">
              {incident.description}
            </div>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* 2. ANÁLISIS IA (GEMINI) */}
            <section className="bg-gradient-to-br from-indigo-50 to-white p-5 rounded-xl border border-indigo-100 shadow-sm">
              <h3 className="text-indigo-900 font-bold mb-4 flex items-center gap-2">
                <Icons.Robot className="h-5 w-5" /> Análisis Contextual (IA)
              </h3>

              {gemini ? (
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-semibold text-slate-600">Confianza del modelo</span>
                      <span className="text-indigo-600 font-bold">{gemini.confidence ? (gemini.confidence * 100).toFixed(0) : 0}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-1.5">
                      <div className="bg-indigo-600 h-1.5 rounded-full" style={{ width: `${(gemini.confidence || 0) * 100}%` }}></div>
                    </div>
                  </div>

                  <div className="text-sm text-slate-700 bg-white p-3 rounded border border-indigo-50 shadow-sm">
                    {gemini.risk_assessment || gemini.explanation || "Sin explicación detallada disponible."}
                  </div>

                  {gemini.recommended_action && (
                    <div className="flex gap-2 items-start text-sm text-indigo-800 bg-indigo-50 p-2 rounded">
                      <Icons.Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
                      <p><strong>Recomendación:</strong> {gemini.recommended_action}</p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-slate-400 italic text-sm">Análisis IA no disponible.</p>
              )}
            </section>

            {/* 3. VIRUSTOTAL */}
            <section className="bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-slate-800 font-bold mb-4 flex items-center gap-2">
                <Icons.Search className="h-5 w-5" /> Análisis de URL (VirusTotal)
              </h3>

              {vt ? (
                !vt.error ? (
                  <div className="space-y-3">
                    <p className="text-xs text-slate-500 break-all border-b pb-2 mb-2">{vt.url}</p>
                    <div className="flex gap-4">
                      <div className="flex-1 text-center bg-white p-3 rounded border border-slate-200">
                        <span className={`block text-2xl font-bold ${vt.positives > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {vt.positives}
                        </span>
                        <span className="text-[10px] uppercase text-slate-400 font-bold">Detecciones</span>
                      </div>
                      <div className="flex-1 text-center bg-white p-3 rounded border border-slate-200">
                        <span className="block text-2xl font-bold text-slate-700">{vt.total}</span>
                        <span className="text-[10px] uppercase text-slate-400 font-bold">Motores Totales</span>
                      </div>
                    </div>
                    {vt.permalink && (
                      <a href={vt.permalink} target="_blank" rel="noreferrer" className="block text-center text-xs text-blue-600 hover:underline mt-2">
                        Ver reporte completo ↗
                      </a>
                    )}
                  </div>
                ) : (
                  <p className="text-orange-600 text-sm bg-orange-50 p-2 rounded">{vt.error}</p>
                )
              ) : (
                <p className="text-slate-400 italic text-sm">Sin URL analizada.</p>
              )}
            </section>
          </div>

          {/* 4. GESTIÓN (ACCIONES) */}
          <section className="border-t border-slate-100 pt-6">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Gestión del Incidente</h3>
            <div className="bg-blue-50 p-5 rounded-xl border border-blue-100 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <div className="md:col-span-1">
                <label className="block text-xs font-bold text-blue-900 mb-1">Estado</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full p-2 border border-blue-200 rounded-md focus:ring-2 focus:ring-blue-500 text-sm"
                >
                  <option value="Nuevo">Nuevo</option>
                  <option value="En Proceso">En Proceso</option>
                  <option value="Resuelto">Resuelto</option>
                  <option value="Cerrado">Cerrado</option>
                  <option value="Falso Positivo">Falso Positivo</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-bold text-blue-900 mb-1">Notas del Analista</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Agrega notas sobre la resolución..."
                    className="flex-1 p-2 border border-blue-200 rounded-md focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                  <button
                    onClick={handleUpdate}
                    disabled={updating}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap"
                  >
                    {updating ? <Icons.Refresh className="h-4 w-4 animate-spin" /> : <Icons.Check className="h-4 w-4" />}
                    Actualizar
                  </button>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}

export default IncidentAnalysisModal;