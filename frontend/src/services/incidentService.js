export const submitIncident = async (incidentData) => {
  const response = await fetch('http://localhost:8000/api/create-report/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(incidentData)
  });

  if (!response.ok) {
    throw new Error('Error al enviar el incidente');
  }

  return response.json();
};

export const getIncidents = async () => {
  const response = await fetch('http://localhost:8000/api/incidents/');
  if (!response.ok) {
    throw new Error('Error al obtener incidentes');
  }
  return response.json();
};
