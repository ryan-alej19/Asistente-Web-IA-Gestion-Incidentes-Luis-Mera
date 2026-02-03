import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const EmployeeDashboard = () => {
  const navigate = useNavigate();
  const [analysisType, setAnalysisType] = useState('url'); // url | file
  const [url, setUrl] = useState('');
  const [attachedFile, setAttachedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [urlTimeout, setUrlTimeout] = useState(null);

  // Analysis State
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
      setAnalysisResult(null);
    }
  };

  const handleUrlChange = (e) => {
    const newUrl = e.target.value;
    setUrl(newUrl);

    // Si es URL válida, analizar automáticamente después de 1 segundo
    if (newUrl && newUrl.includes('.')) {
      if (urlTimeout) clearTimeout(urlTimeout);

      const timeout = setTimeout(() => {
        // Llamada directa a analizar (debemos asegurar que use la nueva URL)
        // Como handleAnalyze usa el estado 'url', y setUrl es async, 
        // pasamos la url explícitamente o dependemos del re-render.
        // Para evitar problemas de closure, mejor usamos una función dedicada o useEffect,
        // pero aquí simularemos el click en "Analizar".
        // Mejor opción: llamar a una versión modificada de analizar recibiendo argumento
        // O simplemente confiar en que el usuario dejará de escribir.
        // Vamos a llamar a analyzeUrlDirect(newUrl)
        analyzeUrlDirect(newUrl);
      }, 1000);

      setUrlTimeout(timeout);
    }
  };

  const analyzeUrlDirect = async (urlToAnalyze) => {
    if (!urlToAnalyze) return;
    setAnalyzing(true);
    setAnalysisResult(null);
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Token ${token}` } };
      const res = await axios.post('http://localhost:8000/api/incidents/analyze-url-preview/', { url: urlToAnalyze }, config);
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(err);
      // No alertar en auto-análisis para no molestar
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    if (analysisType === 'url' && !url) return;
    if (analysisType === 'file' && !attachedFile) return;

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Token ${token}` } };

      let res;
      if (analysisType === 'url') {
        res = await axios.post('http://localhost:8000/api/incidents/analyze-url-preview/', { url }, config);
      } else {
        const formData = new FormData();
        formData.append('file', attachedFile);
        res = await axios.post('http://localhost:8000/api/incidents/analyze-file-preview/', formData, config);
      }
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error al analizar. Intente nuevamente.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSubmitIncident = async () => {
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('incident_type', analysisType);
      formData.append('description', description);
      if (analysisType === 'url') formData.append('url', url);
      if (analysisType === 'file') formData.append('file', attachedFile);

      await axios.post('http://localhost:8000/api/incidents/create/', formData, {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      alert('Incidente reportado exitosamente. El equipo de seguridad lo revisará.');
      setAnalysisResult(null);
      setUrl('');
      setAttachedFile(null);
      setDescription('');
    } catch (err) {
      console.error(err);
      alert('Error al reportar incidente.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex font-sans">
      {/* FORMULARIO - IZQUIERDA (60%) */}
      <div className="w-3/5 p-8 overflow-y-auto">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Panel de Seguridad
              </h1>
              <p className="text-slate-400 text-lg">
                Reporte de correos y archivos sospechosos
              </p>
            </div>
            <button onClick={handleLogout} className="text-slate-400 hover:text-white transition-colors flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Salir
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => { setAnalysisType('url'); setAnalysisResult(null); }}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${analysisType === 'url'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              Enlace Sospechoso
            </button>
            <button
              onClick={() => { setAnalysisType('file'); setAnalysisResult(null); }}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${analysisType === 'file'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
              Archivo Adjunto
            </button>
          </div>

          {/* Formulario dinámico */}
          {analysisType === 'url' ? (
            <div className="mb-6">
              <label className="block text-white font-semibold mb-3 text-lg">
                Pegue el enlace sospechoso:
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="text-slate-500">https://</span>
                </div>
                <input
                  type="text"
                  value={url}
                  onChange={handleUrlChange}
                  placeholder="ejemplo-sospechoso.com"
                  className="w-full pl-20 px-4 py-4 rounded-lg text-lg bg-slate-800 text-white border-2 border-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
              <button
                onClick={handleAnalyze}
                disabled={!url || analyzing}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed disabled:text-slate-500 text-white font-bold py-4 rounded-lg text-lg transition-all flex items-center justify-center gap-2"
              >
                {analyzing ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analizando...
                  </>
                ) : 'Analizar Riesgo Ahora'}
              </button>
            </div>
          ) : (
            <div className="mb-6">
              <label className="block text-white font-semibold mb-3 text-lg">
                Suba el archivo sospechoso:
              </label>
              {!attachedFile ? (
                <label className="flex flex-col items-center justify-center w-full h-48 border-3 border-dashed border-slate-600 rounded-xl cursor-pointer bg-slate-800 hover:bg-slate-750 hover:border-blue-500 transition-all group">
                  <svg className="w-16 h-16 text-slate-500 group-hover:text-blue-500 transition-colors mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-slate-400 font-medium text-lg group-hover:text-white transition-colors">Click para seleccionar archivo</p>
                  <p className="text-slate-500 text-sm mt-2">PDF, EXE, ZIP, DOC, etc.</p>
                  <input type="file" className="hidden" onChange={handleFileChange} />
                </label>
              ) : (
                <div className="bg-slate-800 border-2 border-slate-700 p-6 rounded-xl animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 bg-blue-600 rounded-lg flex items-center justify-center">
                        <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-semibold text-white text-lg">{attachedFile.name}</p>
                        <p className="text-slate-400">{(attachedFile.size / 1024).toFixed(2)} KB</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleAnalyze}
                        disabled={analyzing}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                      >
                        {analyzing ? '...' : 'Analizar'}
                      </button>
                      <button
                        onClick={() => {
                          setAttachedFile(null);
                          setAnalysisResult(null);
                        }}
                        className="px-4 py-2 bg-slate-700 hover:bg-red-600 text-white font-semibold rounded-lg transition-colors"
                      >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Descripción */}
          <div className="mb-6">
            <label className="block text-white font-semibold mb-3 text-lg">
              Descripción (Opcional):
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Cuéntanos qué pasó o por qué sospechas..."
              rows={4}
              className="w-full px-4 py-3 rounded-lg bg-slate-800 text-white border-2 border-slate-700 focus:border-blue-500 focus:outline-none resize-none transition-colors"
            />
          </div>

          {/* Botón enviar */}
          {analysisResult && (
            <button
              onClick={handleSubmitIncident}
              disabled={submitting}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 rounded-lg text-lg transition-colors shadow-lg shadow-green-900/30 flex items-center justify-center gap-2"
            >
              {submitting ? 'Enviando...' : (
                <>
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Crear Reporte de Seguridad
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* PANEL ANÁLISIS - DERECHA (40%) */}
      <div className="w-2/5 bg-slate-950 border-l border-slate-800 p-8 flex flex-col h-screen sticky top-0">
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/50">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">
                Resultado del Análisis
              </h2>
              <p className="text-slate-400 text-sm">
                Motor de Inteligencia Artificial
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center">
          {/* Loading */}
          {analyzing && (
            <div className="text-center">
              <div className="animate-spin w-20 h-20 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-6"></div>
              <p className="text-xl font-semibold text-white mb-2">
                Analizando Amenazas...
              </p>
              <p className="text-slate-400">
                Consultando VirusTotal y bases de datos <br /> de seguridad global...
              </p>
            </div>
          )}

          {/* Resultado CRÍTICO */}
          {analysisResult && (analysisResult.risk_level === 'CRITICAL' || analysisResult.risk_level === 'HIGH' || analysisResult.risk_level === 'MEDIUM') && !analyzing && (
            <div className="w-full">
              <div className="bg-gradient-to-br from-red-900 to-red-950 p-8 rounded-2xl border-4 border-red-500 shadow-2xl shadow-red-900/50">
                <div className="text-center mb-6">
                  {/* Icono de alerta */}
                  <svg className="w-24 h-24 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>

                  <h3 className="text-4xl font-black text-white mb-3 tracking-wide">
                    {analysisResult.risk_level === 'CRITICAL' ? 'PELIGRO' : 'ADVERTENCIA'}
                  </h3>
                  <p className="text-2xl text-red-200 mb-6 font-medium">
                    {analysisResult.message}
                  </p>
                </div>

                <div className="bg-red-950 bg-opacity-80 p-6 rounded-xl mb-6 border border-red-800">
                  <p className="text-xl font-bold text-white mb-3 text-center flex items-center justify-center gap-2">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                    NO ABRIR ESTE ARCHIVO
                  </p>
                  <p className="text-lg text-red-200 text-center">
                    {analysisResult.detail}
                  </p>
                  {analysisResult.source && (
                    <div className="mt-2 text-sm text-red-300 text-center">
                      Detectado por: {analysisResult.source}
                    </div>
                  )}

                  {/* NUEVO: Explicación Gemini */}
                  {analysisResult.gemini_explicacion && (
                    <div className="mt-6 bg-red-800 bg-opacity-40 p-6 rounded-xl border-2 border-red-600">
                      <div className="flex items-start gap-3 mb-3">
                        <svg className="w-6 h-6 text-red-300 flex-shrink-0 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                          <p className="text-white font-semibold mb-2">
                            ¿Qué significa esto?
                          </p>
                          <p className="text-red-100 text-lg leading-relaxed">
                            {analysisResult.gemini_explicacion}
                          </p>
                        </div>
                      </div>

                      {analysisResult.gemini_recomendacion && (
                        <div className="mt-4 pt-4 border-t border-red-700">
                          <p className="text-red-200 font-semibold mb-2">
                            Recomendación:
                          </p>
                          <p className="text-red-100 text-lg">
                            {analysisResult.gemini_recomendacion}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="bg-red-900 bg-opacity-40 p-6 rounded-xl border border-red-800/50">
                  <p className="font-bold text-white mb-3 text-lg border-b border-red-700 pb-2">
                    Acciones Recomendadas:
                  </p>
                  <div className="space-y-3 text-red-100">
                    <div className="flex items-start gap-3">
                      <div className="bg-red-500 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">1</div>
                      <p>Crear reporte inmediatamente (Botón verde)</p>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-red-500 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">2</div>
                      <p>No ejecutar ni descargar el contenido.</p>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-red-500 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">3</div>
                      <p>Esperar contacto del equipo de seguridad.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Resultado SEGURO */}
          {analysisResult && analysisResult.risk_level === 'LOW' && !analyzing && (
            <div className="w-full">
              <div className="bg-gradient-to-br from-green-900 to-green-950 p-8 rounded-2xl border-4 border-green-500 shadow-2xl shadow-green-900/50">
                <div className="text-center">
                  {/* Icono check */}
                  <svg className="w-24 h-24 text-green-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>

                  <h3 className="text-4xl font-black text-white mb-3">
                    SEGURO
                  </h3>
                  <p className="text-xl text-green-200 mb-6 font-medium">
                    {analysisResult.message}
                  </p>

                  <div className="bg-green-950 bg-opacity-80 p-6 rounded-xl border border-green-800">
                    <p className="text-lg text-green-100 flex items-center justify-center gap-2">
                      <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {analysisResult.detail}
                    </p>
                    {analysisResult.source && (
                      <div className="mt-2 text-sm text-gray-400">
                        Analizado con: {analysisResult.source}
                      </div>
                    )}
                  </div>

                  {/* NUEVO: Explicación Gemini */}
                  {analysisResult.gemini_explicacion && (
                    <div className="mt-6 bg-green-800 bg-opacity-40 p-6 rounded-xl border-2 border-green-600">
                      <div className="flex items-start gap-3">
                        <svg className="w-6 h-6 text-green-300 flex-shrink-0 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                          <p className="text-green-100 text-lg leading-relaxed">
                            {analysisResult.gemini_explicacion}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Estado inicial */}
          {!analyzing && !analysisResult && (
            <div className="text-center py-16 opacity-50">
              <svg className="w-32 h-32 text-slate-600 mx-auto mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-slate-400 text-xl font-light">
                Pegue un enlace o suba un archivo<br />para iniciar el análisis de seguridad.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;
