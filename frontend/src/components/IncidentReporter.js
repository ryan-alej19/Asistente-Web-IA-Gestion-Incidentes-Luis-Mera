import React, { useState } from 'react';
import './IncidentReporter.css';
import { submitIncident } from '../services/incidentService';

function IncidentReporter() {
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('medium');
  const [threatType, setThreatType] = useState('malware');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await submitIncident({
        description,
        severity,
        threat_type: threatType
      });
      setMessage('✅ Incidente reportado exitosamente');
      setDescription('');
      setSeverity('medium');
      setThreatType('malware');
    } catch (error) {
      setMessage('❌ Error al reportar incidente');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="incident-reporter">
      <h2>Reportar Incidente de Seguridad</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Descripción del Incidente</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            placeholder="Describe qué sucedió..."
          />
        </div>

        <div className="form-group">
          <label>Severidad</label>
          <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
            <option value="critical">Crítica</option>
          </select>
        </div>

        <div className="form-group">
          <label>Tipo de Amenaza</label>
          <select value={threatType} onChange={(e) => setThreatType(e.target.value)}>
            <option value="malware">Malware</option>
            <option value="phishing">Phishing</option>
            <option value="ransomware">Ransomware</option>
            <option value="otros">Otros</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Enviando...' : 'Reportar Incidente'}
        </button>
      </form>

      {message && <p className={message.includes('✅') ? 'success' : 'error'}>{message}</p>}
    </div>
  );
}

export default IncidentReporter;
