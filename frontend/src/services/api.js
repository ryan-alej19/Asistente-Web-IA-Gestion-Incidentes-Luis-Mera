/**
 * 🔌 API SERVICE - TESIS CIBERSEGURIDAD
 * Ryan Gallegos Mera - PUCEI
 * Backend: http://localhost:8000
 */

const API_URL = 'http://localhost:8000/api';

// ========================================
// 🔐 AUTENTICACIÓN
// ========================================

export const getToken = () => localStorage.getItem('access_token');
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

const getAuthHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': getToken() ? `Bearer ${getToken()}` : ''
});

export const loginUser = async (username, password) => {
  try {
    const response = await fetch(`${API_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      return { success: true, data };
    } else {
      return { success: false, error: data.detail || 'Credenciales inválidas' };
    }
  } catch (error) {
    return { success: false, error: 'Error de conexión con el servidor' };
  }
};

export const logoutUser = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

export const isAuthenticated = () => getToken() !== null;

// ========================================
// 🚨 INCIDENTES
// ========================================

export const getIncidents = async () => {
  try {
    const response = await fetch(`${API_URL}/incidents/`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    const data = await response.json();
    return response.ok ? { success: true, data } : { success: false, error: data.detail };
  } catch (error) {
    return { success: false, error: 'Error de conexión' };
  }
};

export const getIncidentDetail = async (id) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    const data = await response.json();
    return response.ok ? { success: true, data } : { success: false, error: data.detail };
  } catch (error) {
    return { success: false, error: 'Error de conexión' };
  }
};

export const createIncident = async (incidentData) => {
  try {
    const response = await fetch(`${API_URL}/incidents/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(incidentData)
    });

    const data = await response.json();
    return response.ok ? { success: true, data } : { success: false, error: data.error };
  } catch (error) {
    return { success: false, error: 'Error de conexión' };
  }
};

export const updateIncident = async (id, updates) => {
  try {
    const response = await fetch(`${API_URL}/incidents/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    });

    const data = await response.json();
    return response.ok ? { success: true, data } : { success: false, error: data.error };
  } catch (error) {
    return { success: false, error: 'Error de conexión' };
  }
};

// ========================================
// 📈 DASHBOARD
// ========================================

export const getDashboardStats = async () => {
  try {
    const response = await fetch(`${API_URL}/dashboard/stats/`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    const data = await response.json();
    return response.ok ? { success: true, data } : { success: false, error: data.detail };
  } catch (error) {
    return { success: false, error: 'Error de conexión' };
  }
};

// ========================================
// 🤖 IA CLASIFICADOR
// ========================================

export const classifyIncident = async (incidentData) => {
  try {
    const response = await fetch(`${API_URL}/classify/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(incidentData)
    });

    const data = await response.json();
    return response.ok ? { success: true, data } : { success: false, error: data.error };
  } catch (error) {
    return { success: false, error: 'Error de conexión' };
  }
};
