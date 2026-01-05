/**
 * 🛡️ CREAR INCIDENTE CON IA - TESIS CIBERSEGURIDAD
 * Ryan Gallegos Mera - PUCESI
 * Última actualización: 03 de Enero, 2026
 */

import React, { useState } from 'react';
import { createIncident } from '../services/api';
import './CreateIncident.css';

function CreateIncident() {
  const [formData, setFormData] = useState({
    incident_type: '',
    description: '',
    url: ''
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('📤 Enviando incidente...');
      
      const response = await createIncident(formData);
      
      console.log('✅ Respuesta:', response);
      setResult(response);

      // Limpiar formulario
      setFormData({
        incident_type: '',
        description: '',
        url: ''
      });

    } catch (err) {
      console.error('❌ Error:', err);
      setError(err.error || 'Error al crear el incidente');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-incident-container">
      <h2>📋 Reportar Incidente de Seguridad</h2>

      <form onSubmit={handleSubmit} className="incident-form">
        {/* Tipo de Incidente */}
        <div className="form-group">
          <label>Tipo de Incidente *</label>
          <select
            name="incident_type"
            value={formData.incident_type}
            onChange={handleChange}
            required
          >
            <option value="">Seleccione un tipo</option>
            <option value="Phishing">🎣 Phishing</option>
            <option value="Malware">🦠 Malware</option>
            <option value="Acceso no autorizado">🚫 Acceso no autorizado</option>
            <option value="Fuga de datos">💾 Fuga de datos</option>
            <option value="Denegación de servicio">⚠️ Denegación de servicio</option>
            <option value="Otro">📌 Otro</option>
          </select>
        </div>

        {/* Descripción */}
        <div className="form-group">
          <label>Descripción del Incidente *</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describa el incidente de manera detallada..."
            rows="5"
            required
          />
        </div>

        {/* URL (opcional) */}
        <div className="form-group">
          <label>URL Sospechosa (opcional)</label>
          <input
            type="url"
            name="url"
            value={formData.url}
            onChange={handleChange}
            placeholder="https://ejemplo-sospechoso.com"
          />
          <small>Si el incidente involucra una URL, ingrésela aquí para análisis con VirusTotal</small>
        </div>

        {/* Botón de envío */}
        <button 
          type="submit" 
          className="btn-submit"
          disabled={loading}
        >
          {loading ? '⏳ Analizando con IA...' : '🤖 Analizar y Crear Incidente'}
        </button>
      </form>

      {/* Mensaje de error */}
      {error && (
        <div className="alert alert-error">
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      {/* Resultado del análisis */}
      {result && (
        <div className="analysis-results">
          <h3>✅ Incidente Creado y Analizado</h3>

          {/* Información básica */}
          <div className="result-card">
            <h4>📊 Información del Incidente</h4>
            <p><strong>ID:</strong> {result.incident.id}</p>
            <p><strong>Tipo:</strong> {result.incident.incident_type}</p>
            <p><strong>Estado:</strong> {result.incident.status}</p>
            <p>
              <strong>Nivel de Riesgo:</strong>{' '}
              <span className={`badge badge-${result.incident.risk_level.toLowerCase()}`}>
                {result.incident.risk_level}
              </span>
            </p>
          </div>

          {/* Análisis de VirusTotal */}
          {result.virustotal && (
            <div className="result-card">
              <h4>🔍 Análisis de VirusTotal</h4>
              {result.virustotal.error ? (
                <p className="text-warning">{result.virustotal.error}</p>
              ) : (
                <>
                  <p><strong>URL analizada:</strong> {result.virustotal.url}</p>
                  <p>
                    <strong>Detecciones:</strong>{' '}
                    {result.virustotal.positives} / {result.virustotal.total}
                  </p>
                  {result.virustotal.permalink && (
                    <a 
                      href={result.virustotal.permalink} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="btn-link"
                    >
                      Ver reporte completo en VirusTotal
                    </a>
                  )}
                </>
              )}
            </div>
          )}

          {/* Análisis de Gemini AI */}
          {result.gemini && (
            <div className="result-card">
              <h4>🤖 Análisis de IA (Gemini)</h4>
              
              {result.gemini.risk_assessment && (
                <div className="ai-assessment">
                  <h5>📈 Evaluación de Riesgo</h5>
                  <p>{result.gemini.risk_assessment}</p>
                </div>
              )}

              {result.gemini.recommendations && (
                <div className="ai-recommendations">
                  <h5>💡 Recomendaciones</h5>
                  <p>{result.gemini.recommendations}</p>
                </div>
              )}

              {result.gemini.confidence && (
                <p>
                  <strong>Confianza de IA:</strong> {result.gemini.confidence}%
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CreateIncident;
