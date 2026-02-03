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
import { Bar, Pie } from 'react-chartjs-2';

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
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Token ${token}` } };

      const [resIncidents, resStats] = await Promise.all([
        axios.get('http://localhost:8000/api/incidents/list/', config),
        axios.get('http://localhost:8000/api/incidents/stats/', config)
      ]);

      setIncidents(resIncidents.data);
      setStats(resStats.data);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };

  const updateStatus = async (id, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await axios.patch(`http://localhost:8000/api/incidents/${id}/update-status/`, { status: newStatus }, {
        headers: { Authorization: `Token ${token}` }
      });
      fetchData(); // Recargar datos
      setSelectedIncident(null); // Cerrar modal si está abierto
    } catch (err) {
      console.error(err);
      alert('Error actualizando estado');
    }
  };

  const downloadPDF = async (id) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/api/incidents/${id}/pdf/`, {
        headers: { Authorization: `Token ${token}` },
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `reporte_incidente_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Error downloading PDF", err);
      alert('Error descargando PDF');
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

      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem', marginBottom: '2rem' }}>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', height: 'fit-content' }}>
            <div className="card" style={{ textAlign: 'center' }}>
              <h4 style={{ color: 'var(--text-secondary)' }}>Total Incidentes</h4>
              <p style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'white' }}>{stats.total}</p>
            </div>
            <div className="card" style={{ textAlign: 'center', borderColor: '#eab308' }}>
              <h4 style={{ color: '#eab308' }}>Pendientes</h4>
              <p style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#fef08a' }}>{stats.pending}</p>
            </div>
            <div className="card" style={{ textAlign: 'center', borderColor: '#ef4444' }}>
              <h4 style={{ color: '#ef4444' }}>Críticos</h4>
              <p style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#fecaca' }}>{stats.critical}</p>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h4>Tipos de Amenaza</h4>
            <div style={{ width: '200px', height: '200px' }}>
              <Pie data={{
                labels: ['Archivos', 'URLs'],
                datasets: [{
                  data: [stats.by_type.files, stats.by_type.urls],
                  backgroundColor: ['#3b82f6', '#8b5cf6'],
                  borderColor: '#1e293b',
                  borderWidth: 2
                }]
              }} options={{ plugins: { legend: { position: 'bottom', labels: { color: 'white' } } } }} />
            </div>
          </div>
        </div>
      )}

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

                <div style={{ marginTop: '1.5rem', borderTop: '1px solid #334155', paddingTop: '1rem' }}>
                  <h4>Gestionar Estado:</h4>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <button onClick={() => updateStatus(selectedIncident.id, 'pending')} className="btn" style={{ background: '#334155' }}>Pendiente</button>
                    <button onClick={() => updateStatus(selectedIncident.id, 'in_progress')} className="btn" style={{ background: '#0284c7' }}>En Progreso</button>
                    <button onClick={() => updateStatus(selectedIncident.id, 'resolved')} className="btn" style={{ background: '#16a34a' }}>Resolver</button>
                    <button onClick={() => updateStatus(selectedIncident.id, 'closed')} className="btn" style={{ background: '#475569' }}>Cerrar</button>
                  </div>
                </div>
              </div>
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'right', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button
                className="btn"
                style={{ background: '#ef4444', color: 'white' }}
                onClick={() => downloadPDF(selectedIncident.id)}
              >
                📄 Descargar Reporte PDF
              </button>
              <button className="btn btn-primary" onClick={() => setSelectedIncident(null)}>Cerrar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalystDashboard;
