/**
 * 📊 LISTA DE INCIDENTES - TESIS CIBERSEGURIDAD
 * Ryan Gallegos Mera - PUCESI
 * Última actualización: 04 de Enero, 2026
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './IncidentList.css';

function IncidentList() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('todos'); // filtro por estado

  // 🔄 Cargar incidentes al montar el componente
  useEffect(() => {
    fetchIncidents();
  }, []);

  // 📡 Obtener incidentes del backend
  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/incidents/');
      setIncidents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error al cargar incidentes:', error);
      setLoading(false);
    }
  };

  // 🎨 Obtener clase CSS según severidad
  const getSeverityClass = (severity) => {
    const classes = {
      'Alta': 'severity-high',
      'Media': 'severity-medium',
      'Baja': 'severity-low'
    };
    return classes[severity] || 'severity-low';
  };

  // 🎨 Obtener clase CSS según estado
  const getStatusClass = (status) => {
    const classes = {
      'abierto': 'status-open',
      'en_proceso': 'status-progress',
      'resuelto': 'status-resolved',
      'cerrado': 'status-closed'
    };
    return classes[status] || 'status-open';
  };

  // 🔍 Filtrar incidentes por estado
  const filteredIncidents = incidents.filter(incident => {
    if (filter === 'todos') return true;
    return incident.status === filter;
  });

  // 📅 Formatear fecha
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-EC', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="incident-list-container">
      <div className="incident-list-header">
        <h1>📊 Gestión de Incidentes</h1>
        <button onClick={() => window.location.href = '/crear-incidente'} className="btn-new-incident">
          ➕ Nuevo Incidente
        </button>
      </div>

      {/* 🔍 FILTROS */}
      <div className="filters">
        <button 
          className={filter === 'todos' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('todos')}
        >
          📋 Todos ({incidents.length})
        </button>
        <button 
          className={filter === 'abierto' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('abierto')}
        >
          🔓 Abiertos ({incidents.filter(i => i.status === 'abierto').length})
        </button>
        <button 
          className={filter === 'en_proceso' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('en_proceso')}
        >
          ⚙️ En Proceso ({incidents.filter(i => i.status === 'en_proceso').length})
        </button>
        <button 
          className={filter === 'resuelto' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('resuelto')}
        >
          ✅ Resueltos ({incidents.filter(i => i.status === 'resuelto').length})
        </button>
      </div>

      {/* 📊 TABLA DE INCIDENTES */}
      {loading ? (
        <div className="loading">🔄 Cargando incidentes...</div>
      ) : (
        <div className="table-container">
          <table className="incidents-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Tipo</th>
                <th>Descripción</th>
                <th>Severidad</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredIncidents.length === 0 ? (
                <tr>
                  <td colSpan="7" className="no-data">
                    📭 No hay incidentes registrados
                  </td>
                </tr>
              ) : (
                filteredIncidents.map((incident, index) => (
                  <tr key={incident.id}>
                    <td>{index + 1}</td>
                    <td>
                      <span className="incident-type">{incident.incident_type}</span>
                    </td>
                    <td className="description-cell">
                      {incident.description.substring(0, 80)}...
                    </td>
                    <td>
                      <span className={`severity-badge ${getSeverityClass(incident.severity)}`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${getStatusClass(incident.status)}`}>
                        {incident.status === 'en_proceso' ? 'En Proceso' : incident.status}
                      </span>
                    </td>
                    <td>{formatDate(incident.created_at)}</td>
                    <td>
                      <button className="btn-view" title="Ver detalles">
                        👁️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default IncidentList;
