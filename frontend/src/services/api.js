/**
 * 🛡️ API SERVICE - TESIS CIBERSEGURIDAD
 * Ryan Gallegos Mera - PUCESI
 * Última actualización: 03 de Enero, 2026
 */

import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Configurar interceptor para agregar token a todas las peticiones
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ========================================
// 🔐 AUTENTICACIÓN
// ========================================

export const login = async (email, password) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login/`, {
      email,
      password
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Error al iniciar sesión' };
  }
};

export const register = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/auth/register/`, userData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Error al registrar usuario' };
  }
};

// ========================================
// 📋 INCIDENTES
// ========================================

export const createIncident = async (incidentData) => {
  try {
    console.log('📤 Enviando incidente:', incidentData);
    
    const response = await axios.post(`${API_URL}/incidents/create/`, incidentData);
    
    console.log('✅ Respuesta recibida:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error al crear incidente:', error);
    throw error.response?.data || { error: 'Error al crear incidente' };
  }
};

export const getIncidents = async () => {
  try {
    const response = await axios.get(`${API_URL}/incidents/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Error al obtener incidentes' };
  }
};

export const getIncidentDetail = async (incidentId) => {
  try {
    const response = await axios.get(`${API_URL}/incidents/${incidentId}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Error al obtener detalle del incidente' };
  }
};

export const updateIncidentStatus = async (incidentId, updateData) => {
  try {
    const response = await axios.patch(
      `${API_URL}/incidents/${incidentId}/status/`,
      updateData
    );
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Error al actualizar incidente' };
  }
};

export const getDashboardStats = async () => {
  try {
    const response = await axios.get(`${API_URL}/incidents/stats/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Error al obtener estadísticas' };
  }
};

export default {
  login,
  register,
  createIncident,
  getIncidents,
  getIncidentDetail,
  updateIncidentStatus,
  getDashboardStats
};
