import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, Link, FileText, Upload, X, CheckCircle,
  AlertTriangle, AlertOctagon, Info, ArrowRight, Loader2, LogOut
} from 'lucide-react';
import { GeminiLogo, VirusTotalLogo, MetaDefenderLogo } from '../components/BrandLogos';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import API_URL from '../config/api';

const EmployeeDashboard = () => {
  // Guardamos si el usuario elige analizar URL o Archivo
  const [analysisType, setAnalysisType] = useState('url');
  const [url, setUrl] = useState('');
  const [attachedFile, setAttachedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [urlTimeout, setUrlTimeout] = useState(null);

  // Estados para controlar la carga y el resultado del análisis
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Estado para el efecto de "escribiendo" en la explicación de la IA
  const [typwriterText, setTypewriterText] = useState('');

  // Función para salir del sistema (Cerrar Sesión)
  const handleLogout = () => {
    localStorage.clear(); // Borra el token guardado
    window.location.href = '/login'; // Redirige al login
  };

  // Función que se activa al elegir un archivo del computador
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setAttachedFile(file);
      setAnalysisResult(null); // Resetea resultados anteriores
    }
  };

  // Función que se activa al escribir en la caja de URL
  const handleUrlChange = (e) => {
    const newUrl = e.target.value;
    setUrl(newUrl);

    // Si parece una URL válida (tiene un punto), esperamos un segundo y analizamos automáticamente
    if (newUrl && newUrl.includes('.')) {
      if (urlTimeout) clearTimeout(urlTimeout);
      const timeout = setTimeout(() => {
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
      const res = await axios.post(`${API_URL}/api/incidents/analyze-url-preview/`, { url: urlToAnalyze }, config);
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    if (analysisType === 'url' && !url) return;
    if (analysisType === 'file' && !attachedFile) return;

    setAnalyzing(true);
    setAnalysisResult(null);
    setTypewriterText('');

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Token ${token}` } };
      let res;
      if (analysisType === 'url') {
        res = await axios.post(`${API_URL}/api/incidents/analyze-url-preview/`, { url }, config);
      } else {
        const formData = new FormData();
        formData.append('file', attachedFile);
        res = await axios.post(`${API_URL}/api/incidents/analyze-file-preview/`, formData, config);
      }
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error al analizar. Intente nuevamente.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Typewriter Effect for Gemini Explanation
  useEffect(() => {
    if (analysisResult?.gemini_result?.explicacion || analysisResult?.gemini_explicacion) {
      const text = analysisResult.gemini_explicacion || analysisResult.gemini_result.explicacion;
      if (!text) return;
      let i = 0;
      const speed = 15; // ms per char

      const type = () => {
        if (i < text.length) {
          setTypewriterText((prev) => text.substring(0, i + 1));
          i++;
          setTimeout(type, speed);
        }
      };

      setTypewriterText('');
      type();
    }
  }, [analysisResult]);

  const handleSubmitIncident = async () => {
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('incident_type', analysisType);
      formData.append('description', description);
      if (analysisType === 'url') formData.append('url', url);
      if (analysisType === 'file') formData.append('file', attachedFile);

      // Enviar el resultado del análisis (snapshot)
      if (analysisResult) {
        const snapshot = {
          engines: analysisResult.engines,
          risk_level: analysisResult.risk_level,
          gemini_explicacion: analysisResult.gemini_explicacion || (analysisResult.gemini_result?.explicacion),
          gemini_recomendacion: analysisResult.gemini_recomendacion || (analysisResult.gemini_result?.recomendacion),
          heuristic: analysisResult.heuristic,
          positives: analysisResult.positives || analysisResult.total_positives,
          total: analysisResult.total || analysisResult.total_engines
        };
        formData.append('analysis_result', JSON.stringify(snapshot));
      }

      await axios.post('http://localhost:8000/api/incidents/create/', formData, {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      alert('Incidente reportado exitosamente. El equipo administrador lo revisará.');
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

  // Variants for Framer Motion
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.3 } }
  };

  // Helper calculation for Chart
  const getChartData = () => {
    if (!analysisResult) return [];
    const positives = analysisResult.positives || analysisResult.total_positives || 0;
    const total = analysisResult.total || analysisResult.total_engines || 1; // avoid div 0
    const clean = Math.max(0, total - positives);

    return [
      { name: 'Malicioso', value: positives, color: '#ef4444' }, // Red-500
      { name: 'Seguro', value: clean, color: '#22c55e' } // Green-500
    ];
  };

  const chartData = getChartData();
  const positivesCount = analysisResult ? (analysisResult.positives || analysisResult.total_positives || 0) : 0;
  const totalCount = analysisResult ? (analysisResult.total || analysisResult.total_engines || 0) : 0;

  return (
    <div className="min-h-screen bg-background text-gray-200 font-sans flex overflow-hidden">

      {/* LEFT PANEL - INPUT FORM */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-3/5 p-8 overflow-y-auto border-r border-border"
      >
        <div className="max-w-3xl mx-auto pt-6">

          <header className="mb-10 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="relative group perspective-1000">
                <div className="absolute inset-0 bg-primary/20 rounded-xl blur-lg group-hover:bg-primary/40 transition-all duration-300" />
                <div className="relative bg-white p-2 rounded-xl shadow-lg border-2 border-white/50 transform transition-transform duration-300 hover:scale-105 hover:rotate-2">
                  <img
                    src="/assets/logo_tecnicontrol.jpg"
                    alt="Tecnicontrol Logo"
                    className="h-14 w-auto object-contain rounded-lg filter drop-shadow-sm"
                  />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center gap-3 tracking-tight">
                  Centro de Seguridad
                </h1>
                <p className="text-secondary text-sm font-medium">
                  Talleres Luis Mera - Software Protegido
                </p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-secondary hover:text-white transition-colors px-4 py-2 hover:bg-surface rounded-lg"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Salir</span>
            </button>
          </header>

          {/* Type Selector */}
          <div className="grid grid-cols-2 gap-4 mb-8 bg-surface p-1 rounded-xl">
            <button
              onClick={() => { setAnalysisType('url'); setAnalysisResult(null); }}
              className={`flex items-center justify-center gap-3 py-4 rounded-lg font-medium transition-all ${analysisType === 'url'
                ? 'bg-primary text-white shadow-lg shadow-primary/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
            >
              <Link className="w-5 h-5" />
              <span>Analizar Enlace</span>
            </button>
            <button
              onClick={() => { setAnalysisType('file'); setAnalysisResult(null); }}
              className={`flex items-center justify-center gap-3 py-4 rounded-lg font-medium transition-all ${analysisType === 'file'
                ? 'bg-primary text-white shadow-lg shadow-primary/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
            >
              <FileText className="w-5 h-5" />
              <span>Analizar Archivo</span>
            </button>
          </div>

          {/* Input Area */}
          <motion.div
            key={analysisType}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="mb-8"
          >
            {analysisType === 'url' ? (
              <div className="relative group">
                <input
                  type="text"
                  value={url}
                  onChange={handleUrlChange}
                  placeholder="Buscar o Escanear URL"
                  className="w-full bg-surface border border-border text-white rounded-xl py-4 px-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-lg font-mono"
                />
              </div>
            ) : (
              <div className="relative">
                {!attachedFile ? (
                  <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-border rounded-xl cursor-pointer bg-surface/50 hover:bg-surface hover:border-primary/50 transition-all group">
                    <Upload className="w-12 h-12 text-gray-500 group-hover:text-primary mb-4 transition-colors" />
                    <p className="text-gray-300 font-medium text-lg">Haga clic o arrastre un archivo aquí</p>
                    <p className="text-gray-500 text-sm mt-2">Soporta PDF, DOCX, EXE, ZIP...</p>
                    <input type="file" className="hidden" onChange={handleFileChange} />
                  </label>
                ) : (
                  <div className="bg-surface border border-border rounded-xl p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary">
                        <FileText className="w-6 h-6" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{attachedFile.name}</p>
                        <p className="text-sm text-gray-400">{(attachedFile.size / 1024).toFixed(2)} KB</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => { setAttachedFile(null); setAnalysisResult(null); }}
                        className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-danger transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>

          {/* Action Button */}
          <div className="flex justify-end">
            <button
              onClick={handleAnalyze}
              disabled={(!url && !attachedFile) || analyzing}
              className="bg-primary hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-3 rounded-xl font-medium text-lg shadow-lg shadow-primary/25 transition-all flex items-center gap-2"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analizando...
                </>
              ) : (
                <>
                  Analizar Riesgo <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          <hr className="border-border my-10" />

          {/* Optional Description */}
          <div className="mb-8">
            <label className="block text-gray-400 font-medium mb-2">Notas adicionales (Opcional):</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Contexto sobre el incidente..."
              rows={3}
              className="w-full bg-surface border border-border text-white rounded-lg p-4 focus:ring-1 focus:ring-primary outline-none resize-none"
            />
          </div>

          {/* Submit Report Button */}
          <AnimatePresence>
            {analysisResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <button
                  onClick={handleSubmitIncident}
                  disabled={submitting}
                  className="w-full bg-success text-white font-bold py-4 rounded-xl shadow-lg shadow-success/20 hover:bg-green-600 transition-all flex items-center justify-center gap-2"
                >
                  {submitting ? <Loader2 className="animate-spin" /> : <Shield className="w-5 h-5" />}
                  {submitting ? 'Enviando...' : 'Generar Incidente'}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* RIGHT PANEL - RESULTS */}
      <div className="w-2/5 bg-surface border-l border-border relative overflow-y-auto custom-scrollbar">
        <div className="p-8 min-h-full flex flex-col">

          <div className="mb-8 flex items-center gap-3">
            <div className="w-10 h-10 bg-background rounded-full flex items-center justify-center border border-border">
              <GeminiLogo className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-white font-bold text-lg">Motor de Análisis</h2>
              <p className="text-xs text-gray-400">Powered by Google Gemini 2.5 Flash • VirusTotal • MetaDefender • Google Safe Browsing</p>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {/* Loading State */}
            {analyzing && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center justify-center text-center opacity-50"
              >
                <div className="relative w-24 h-24 mb-6">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 rounded-full border-4 border-t-primary border-r-transparent border-b-transparent border-l-transparent"
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <GeminiLogo className="w-10 h-10 opacity-80" />
                  </div>
                </div>
                <p className="text-white font-medium text-lg">Analizando Amenazas</p>
                <p className="text-gray-500 text-sm mt-2">Consultando bases de datos globales...</p>
              </motion.div>
            )}

            {/* Results State */}
            {!analyzing && analysisResult && (
              <motion.div
                key="result"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="space-y-6"
              >
                {/* Risk Card */}
                <motion.div
                  variants={cardVariants}
                  className={`relative overflow-hidden rounded-2xl border p-1 text-center ${analysisResult.risk_level === 'CRITICAL' || analysisResult.risk_level === 'HIGH' ? 'bg-danger/10 border-danger text-danger' :
                    analysisResult.risk_level === 'MEDIUM' || analysisResult.risk_level === 'CAUTION' ? 'bg-warning/10 border-warning text-warning' :
                      'bg-success/10 border-success text-success'
                    }`}
                >
                  <div className="flex flex-col items-center p-6">
                    {/* CHART VISUALIZATION */}
                    <div className="w-40 h-40 mb-4 relative">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={chartData}
                            innerRadius={60}
                            outerRadius={75}
                            paddingAngle={5}
                            dataKey="value"
                            stroke="none"
                          >
                            {chartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{ backgroundColor: '#1a1b26', borderColor: '#2f334d', color: '#fff' }}
                            itemStyle={{ color: '#fff' }}
                          />
                        </PieChart>
                      </ResponsiveContainer>

                      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        <span className={`text-2xl font-bold ${analysisResult.risk_level === 'CRITICAL' ? 'text-danger' :
                          analysisResult.risk_level === 'LOW' ? 'text-success' : 'text-warning'
                          }`}>
                          {positivesCount}/{totalCount}
                        </span>
                        <span className="text-xs text-gray-500 uppercase tracking-widest mt-1">Detecciones</span>
                      </div>
                    </div>

                    <h2 className="text-3xl font-black tracking-tight mb-2">
                      {analysisResult.risk_level === 'LOW' ? 'SEGURO' :
                        analysisResult.risk_level === 'CRITICAL' ? 'PELIGROSO' :
                          'PRECAUCIÓN'}
                    </h2>
                    <p className="font-medium opacity-90 text-lg">
                      {analysisResult.message || "Análisis Completado"}
                    </p>
                  </div>
                </motion.div>

                {/* Gemini Analysis */}
                <div className="bg-background rounded-xl p-6 border border-border">
                  <div className="flex items-center gap-2 mb-4">
                    <GeminiLogo className="w-5 h-5" />
                    <h3 className="text-white font-bold">Análisis Inteligente</h3>
                  </div>
                  <p className="text-gray-300 leading-relaxed font-light">
                    {typwriterText}
                    <motion.span
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ repeat: Infinity, duration: 0.8 }}
                      className="inline-block w-1.5 h-4 ml-1 bg-primary align-middle"
                    />
                  </p>
                </div>

                {/* Engines Detail */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Detalle por Motores</h3>
                  </div>

                  {analysisResult.engines?.map((engine, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="bg-background rounded-lg p-4 border border-border flex items-center justify-between group hover:border-primary/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        {engine.name === 'VirusTotal' ? <VirusTotalLogo className="w-8 h-8" /> :
                          engine.name === 'MetaDefender' ? <MetaDefenderLogo className="w-8 h-8" /> :
                            <Shield className="w-8 h-8 text-gray-600" />}

                        <div>
                          <p className="text-white font-medium">{engine.name}</p>
                          <p className={`text-xs font-bold ${engine.detected || (engine.positives > 0) ? 'text-danger' : 'text-success'
                            }`}>
                            {engine.detected || (engine.positives > 0) ? 'Amenaza Detectada' : 'Limpio'}
                          </p>
                          {/* Show x/x for engines that support it */}
                          {(engine.total > 0) && (
                            <p className="text-xs text-gray-500 mt-0.5">
                              {engine.positives}/{engine.total} motores
                            </p>
                          )}
                        </div>
                      </div>

                      {engine.link && (
                        <a
                          href={engine.link}
                          target="_blank"
                          rel="noreferrer"
                          className="text-gray-500 hover:text-primary transition-colors"
                        >
                          <ArrowRight className="w-5 h-5" />
                        </a>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>

    </div>
  );
};

export default EmployeeDashboard;
