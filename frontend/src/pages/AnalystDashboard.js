import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AnalystDashboard = () => {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    fetchIncidents();
  }, []);

  const fetchIncidents = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://localhost:8000/api/incidents/list/', {
        headers: { Authorization: `Token ${token}` }
      });
      setIncidents(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <h1>Centro de Operaciones de Seguridad</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Gestión y análisis avanzado</p>
        </div>
        <div>
          <span className="risk-badge risk-LOW" style={{ marginRight: '1rem', background: '#334155' }}>
            Analista Conectado
          </span>
          <button onClick={handleLogout} className="logout-btn">Salir</button>
        </div>
      </header>

      <div className="card">
        <h3>Incidentes Recientes</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Reportado Por</th>
              <th>Tipo</th>
              <th>Contenido</th>
              <th>Riesgo Detectado</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((inc) => (
              <tr key={inc.id}>
                <td>#{inc.id}</td>
                <td>{inc.reported_by_username || 'Usuario'}</td>
                <td>{inc.incident_type.toUpperCase()}</td>
                <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {inc.url || inc.attached_file}
                </td>
                <td>
                  <span className={`risk-badge risk-${inc.risk_level}`}>
                    {inc.risk_level}
                  </span>
                </td>
                <td>{inc.status}</td>
                <td>{new Date(inc.created_at).toLocaleString()}</td>
                <td>
                  <button
                    className="btn btn-primary"
                    style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
                    onClick={() => setSelectedIncident(inc)}
                  >
                    Ver Detalles
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedIncident && (
        <div className="modal-overlay" onClick={() => setSelectedIncident(null)}>
          <div className="card" style={{ width: '800px', maxHeight: '90vh', overflowY: 'auto' }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2>Detalle del Incidente #{selectedIncident.id}</h2>
              <button className="btn" onClick={() => setSelectedIncident(null)}>
                <svg className="w-6 h-6 text-slate-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div>
                <h4>Información General</h4>
                <p><strong>Reportado por:</strong> {selectedIncident.reported_by_username}</p>
                <p><strong>Fecha:</strong> {new Date(selectedIncident.created_at).toLocaleString()}</p>
                <p><strong>Descripción:</strong> {selectedIncident.description || 'Sin descripción'}</p>
                <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '0.5rem', wordBreak: 'break-all' }}>
                  {selectedIncident.url && <p>URL: <a href={selectedIncident.url} target="_blank" rel="noreferrer" style={{ color: 'var(--primary)' }}>{selectedIncident.url}</a></p>}
                  {selectedIncident.attached_file && <p>Archivo: {selectedIncident.attached_file}</p>}
                </div>
              </div>

              <div>
                <h4>Análisis Técnico</h4>
                <div style={{ marginBottom: '1rem' }}>
                  <p>Nivel de Riesgo:</p>
                  <span className={`risk-badge risk-${selectedIncident.risk_level}`} style={{ fontSize: '1.2rem' }}>
                    {selectedIncident.risk_level}
                  </span>
                </div>

                {selectedIncident.virustotal_result && (
                  <div style={{ fontSize: '0.9rem' }}>
                    <p><strong>VirusTotal:</strong></p>
                    <pre style={{ background: '#0f172a', padding: '0.5rem', borderRadius: '0.3rem', overflow: 'auto' }}>
                      Positivos: {selectedIncident.virustotal_result.positives} / {selectedIncident.virustotal_result.total}
                    </pre>
                  </div>
                )}

                {selectedIncident.phishtank_result && (
                  <div style={{ fontSize: '0.9rem' }}>
                    <p><strong>PhishTank:</strong></p>
                    <pre style={{ background: '#0f172a', padding: '0.5rem', borderRadius: '0.3rem', overflow: 'auto' }}>
                      Phishing: {selectedIncident.phishtank_result.is_phishing ? 'SI' : 'NO'}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'right' }}>
              <button className="btn btn-primary" onClick={() => setSelectedIncident(null)}>Cerrar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalystDashboard;
