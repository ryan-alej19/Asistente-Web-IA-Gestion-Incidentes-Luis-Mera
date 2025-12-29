import React, { useState } from 'react';
import './IncidentReporter.css';
import { submitIncident } from '../services/incidentService';

function IncidentReporter() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await submitIncident({
        description: input,
        threat_type: 'otro' // La IA detectará el tipo real
      });
      
      // Mostrar resultado con lo que IA detectó
      setResult({
        success: true,
        threatType: response.threat_type,
        severity: response.severity,
        confidence: response.confidence
      });
      
      setInput(''); // Limpiar
      
    } catch (error) {
      setResult({
        success: false,
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="incident-reporter">
      <h2>📋 Reportar Incidente de Seguridad</h2>
      <p className="subtitle">Describe lo que sucedió - Nuestro sistema IA analizará automáticamente</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>¿Qué pasó?</label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            required
            placeholder="Ejemplo: 'Recibí un email solicitando verificar mi cuenta urgentemente con un link sospechoso'"
            rows="5"
          />
        </div>

        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? '🔍 Analizando con IA...' : '📤 Reportar Incidente'}
        </button>
      </form>

      {/* Mostrar resultado del análisis IA */}
      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          {result.success ? (
            <>
              <h3>✅ Incidente Procesado</h3>
              <div className="result-details">
                <p><strong>Tipo Detectado:</strong> {result.threatType}</p>
                <p><strong>Severidad:</strong> <span className={`severity-${result.severity}`}>{result.severity.toUpperCase()}</span></p>
                <p><strong>Confianza IA:</strong> {(result.confidence * 100).toFixed(0)}%</p>
              </div>
            </>
          ) : (
            <>
              <h3>❌ Error</h3>
              <p>{result.error}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default IncidentReporter;
