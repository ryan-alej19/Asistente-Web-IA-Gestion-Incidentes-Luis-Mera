/**
 * Servicio de incidentes
 * Comunica con el backend Django para gestionar incidentes
 */
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  
  // Si estamos en IP local, usar esa IP
  if (hostname.includes('192.168')) {
    return `http://${hostname}:8000`;
  }
  
  // Si no, usar localhost (desarrollo local)
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();
const API_URL = `${API_BASE_URL}/api`; 

// ============================================
// FUNCIONES PRINCIPALES
// ============================================

/**
 * Crear nuevo incidente
 * POST /api/incidents/
 */
export const createIncident = async (incidentData) => {
  try {
    const response = await fetch(`${API_URL}/incidents/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: incidentData.title || 'Incidente reportado',
        description: incidentData.description,
        threat_type: incidentData.threat_type || 'otro',
        severity: incidentData.severity || undefined, // Será calculado por IA
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al crear incidente');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error en createIncident:', error);
    throw error;
  }
};

/**
 * Crear incidente desde formulario rápido
 * POST /api/create-report/
 */
export const submitIncident = async (incidentData) => {
  try {
    const response = await fetch(`${API_URL}/create-report/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        description: incidentData.description,
        threat_type: incidentData.threat_type || 'otro',
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error al enviar el incidente');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en submitIncident:', error);
    throw error;
  }
};

/**
 * Obtener todos los incidentes
 * GET /api/incidents/
 */
export const getIncidents = async (filters = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    // Agregar filtros si existen
    if (filters.severity) queryParams.append('severity', filters.severity);
    if (filters.status) queryParams.append('status', filters.status);
    if (filters.threat_type) queryParams.append('threat_type', filters.threat_type);
    if (filters.page) queryParams.append('page', filters.page);
    if (filters.search) queryParams.append('search', filters.search);
    
    const url = `${API_URL}/incidents/?${queryParams.toString()}`;
    
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Error al obtener incidentes');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en getIncidents:', error);
    throw error;
  }
};

/**
 * Obtener detalle de un incidente
 * GET /api/incidents/{id}/
 */
export const getIncidentDetail = async (id) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/`);

    if (!response.ok) {
      throw new Error('Error al obtener detalle del incidente');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en getIncidentDetail:', error);
    throw error;
  }
};

/**
 * Actualizar un incidente
 * PATCH /api/incidents/{id}/
 */
export const updateIncident = async (id, data) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Error al actualizar incidente');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en updateIncident:', error);
    throw error;
  }
};

/**
 * Marcar incidente como resuelto
 * POST /api/incidents/{id}/resolve/
 */
export const resolveIncident = async (id) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/resolve/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Error al resolver incidente');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en resolveIncident:', error);
    throw error;
  }
};

/**
 * Asignar incidente a un usuario
 * POST /api/incidents/{id}/assign/
 */
export const assignIncident = async (id, userId) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/assign/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId }),
    });

    if (!response.ok) {
      throw new Error('Error al asignar incidente');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en assignIncident:', error);
    throw error;
  }
};

/**
 * Eliminar un incidente
 * DELETE /api/incidents/{id}/
 */
export const deleteIncident = async (id) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Error al eliminar incidente');
    }

    return { success: true };
  } catch (error) {
    console.error('Error en deleteIncident:', error);
    throw error;
  }
};

/**
 * Obtener incidentes críticos
 * GET /api/incidents/critical/
 */
export const getCriticalIncidents = async () => {
  try {
    const response = await fetch(`${API_URL}/incidents/critical/`);

    if (!response.ok) {
      throw new Error('Error al obtener incidentes críticos');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en getCriticalIncidents:', error);
    throw error;
  }
};

/**
 * Obtener estadísticas
 * GET /api/incidents/statistics/
 */
export const getStatistics = async () => {
  try {
    const response = await fetch(`${API_URL}/incidents/statistics/`);

    if (!response.ok) {
      throw new Error('Error al obtener estadísticas');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en getStatistics:', error);
    throw error;
  }
};

/**
 * Obtener incidentes recientes (últimas 24h)
 * GET /api/incidents/recent/
 */
export const getRecentIncidents = async () => {
  try {
    const response = await fetch(`${API_URL}/incidents/recent/`);

    if (!response.ok) {
      throw new Error('Error al obtener incidentes recientes');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en getRecentIncidents:', error);
    throw error;
  }
};

/**
 * Resolver múltiples incidentes
 * POST /api/incidents/bulk_resolve/
 */
export const bulkResolveIncidents = async (incidentIds) => {
  try {
    const response = await fetch(`${API_URL}/incidents/bulk_resolve/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ incident_ids: incidentIds }),
    });

    if (!response.ok) {
      throw new Error('Error al resolver múltiples incidentes');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en bulkResolveIncidents:', error);
    throw error;
  }
};

// ============================================
// EXPORTAR TODO COMO OBJETO (alternativa)
// ============================================

const incidentService = {
  createIncident,
  submitIncident,
  getIncidents,
  getIncidentDetail,
  updateIncident,
  resolveIncident,
  assignIncident,
  deleteIncident,
  getCriticalIncidents,
  getStatistics,
  getRecentIncidents,
  bulkResolveIncidents,
};

export default incidentService;
