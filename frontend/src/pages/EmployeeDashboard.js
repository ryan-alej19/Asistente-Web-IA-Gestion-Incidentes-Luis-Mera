import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, Link, FileText, Upload, X, CheckCircle,
  AlertTriangle, AlertOctagon, Info, ArrowRight, Loader2, LogOut, ShieldAlert
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
  const [isDragging, setIsDragging] = useState(false);

  // Estado para el efecto de "escribiendo" en la explicación de la IA
  const [typwriterText, setTypewriterText] = useState('');

  // Estado para notificaciones Toast
  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);

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

      // Auto-detect image
      if (file.type.startsWith('image/')) {
        setAnalysisType('image');
      } else {
        setAnalysisType('file');
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setAttachedFile(file);
      setAnalysisResult(null); // Resetea resultados anteriores

      // Auto-detect image
      if (file.type.startsWith('image/')) {
        setAnalysisType('image');
      } else {
        setAnalysisType('file');
      }
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
    if ((analysisType === 'file' || analysisType === 'image') && !attachedFile) return;

    setAnalyzing(true);
    setAnalysisResult(null);
    setTypewriterText('');

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Token ${token}` } };
      let res;
      if (analysisType === 'url') {
        res = await axios.post(`${API_URL}/api/incidents/analyze-url-preview/`, { url }, config);
      } else if (analysisType === 'file') {
        const formData = new FormData();
        formData.append('file', attachedFile);
        res = await axios.post(`${API_URL}/api/incidents/analyze-file-preview/`, formData, config);
      } else if (analysisType === 'image') {
        const formData = new FormData();
        formData.append('file', attachedFile);
        res = await axios.post(`${API_URL}/api/incidents/analyze-image-preview/`, formData, config);
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
    if (analysisResult?.gemini_result?.explicacion || analysisResult?.gemini_explicacion || analysisResult?.gemini_explanation) {
      const text = analysisResult.gemini_explanation || analysisResult.gemini_explicacion || analysisResult.gemini_result?.explicacion;
      if (!text) return;
      let i = 0;
      const speed = 5; // ms per tick
      const chunkSize = 5; // chars per tick

      const type = () => {
        if (i < text.length) {
          const nextI = Math.min(i + chunkSize, text.length);
          setTypewriterText((prev) => text.substring(0, nextI));
          i = nextI;
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
      if (analysisType === 'file' || analysisType === 'image') formData.append('file', attachedFile);

      // Enviar el resultado del análisis (snapshot)
      if (analysisResult) {
        const snapshot = {
          engines: analysisResult.engines,
          risk_level: analysisResult.risk_level,
          gemini_explicacion: analysisResult.gemini_explanation || analysisResult.gemini_explicacion || (analysisResult.gemini_result?.explicacion),
          gemini_recomendacion: analysisResult.gemini_recommendation || analysisResult.gemini_recomendacion || (analysisResult.gemini_result?.recomendacion),
          heuristic: analysisResult.heuristic,
          positives: analysisResult.positives || analysisResult.total_positives,
          total: analysisResult.total || analysisResult.total_engines
        };
        formData.append('analysis_result', JSON.stringify(snapshot));
      }

      await axios.post(`${API_URL}/api/incidents/create/`, formData, {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // alert('Incidente reportado exitosamente. El equipo administrador lo revisará.');
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 5000); // Ocultar después de 5s
      setAnalysisResult(null);
      setUrl('');
      setAttachedFile(null);
      setDescription('');
      setDescription('');
      setDescription('');
    } catch (err) {
      console.error(err);
      setShowError(true);
      setTimeout(() => setShowError(false), 5000);
    } finally {
      setSubmitting(false);
    }
  };

  // Variants for Framer Motion
  const containerVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.2 } }
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.3 } }
  };

  // Helper calculation for Chart
  const isAdvancedThreat = analysisResult?.engines?.some(e =>
    (e.name === 'Clasificador Heurístico' || e.name === 'Inteligencia Artificial (Gemini Vision)') && e.detected
  ) === true;

  const getChartData = () => {
    if (!analysisResult) return [];
    const positives = analysisResult.positives || analysisResult.total_positives || 0;
    const total = analysisResult.total || analysisResult.total_engines || 1; // avoid div 0
    const clean = Math.max(0, total - positives);

    if (isAdvancedThreat) {
      return [
        { name: 'Malicioso', value: positives, color: '#ef4444' }, // Red-500
        { name: 'Evasión', value: clean, color: '#4b5563' } // Gray-600 pattern for bypassed
      ];
    }

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
                  <span className="text-[10px] bg-primary/20 text-primary border border-primary/30 px-2 py-0.5 rounded-full font-bold">
                    v1.3.0
                  </span>
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
              className={`flex items-center justify-center gap-3 py-4 rounded-lg font-medium transition-all ${(analysisType === 'file' || analysisType === 'image')
                ? 'bg-primary text-white shadow-lg shadow-primary/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
            >
              <FileText className="w-5 h-5" />
              <span>Analizar Archivo / Imagen</span>
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
            ) : (analysisType === 'file' || analysisType === 'image') ? (
              <div className="relative">
                {!attachedFile ? (
                  <label
                    className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 group ${isDragging ? 'bg-primary/20 border-primary scale-[1.02] shadow-[0_0_30px_rgba(59,130,246,0.3)]' : 'border-border bg-surface/50 hover:bg-surface hover:border-primary/50'}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <Upload className={`w-12 h-12 mb-4 transition-all duration-300 ${isDragging ? 'text-primary scale-125 -translate-y-2' : 'text-gray-500 group-hover:text-primary group-hover:-translate-y-1'}`} />
                    <p className={`font-medium text-lg transition-colors ${isDragging ? 'text-primary' : 'text-gray-300'}`}>Haga clic o arrastre un archivo aquí</p>
                    <p className="text-gray-500 text-sm mt-2">{analysisType === 'image' ? 'Soporta PNG, JPG, JPEG...' : 'Soporta PDF, DOCX, EXE, ZIP...'}</p>
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
            ) : null}
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
                {/* Heuristic Detection Flag */}
                {(() => {
                  return (
                    <>
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
                            {analysisResult.risk_level === 'SAFE' ? 'SEGURO' :
                              analysisResult.risk_level === 'LOW' ? 'RIESGO MÍNIMO' :
                                analysisResult.risk_level === 'CRITICAL' ? 'CRÍTICO' :
                                  analysisResult.risk_level === 'HIGH' ? 'ALTO RIESGO' :
                                    'PRECAUCIÓN'}
                          </h2>
                          <p className="font-medium opacity-90 text-lg">
                            {analysisResult.message || "Análisis Completado"}
                          </p>
                        </div>
                      </motion.div>

                      {/* Gemini Analysis */}
                      <div className={`bg-background rounded-xl p-6 border transition-all duration-500 ${isAdvancedThreat ? 'border-danger/80 shadow-[0_0_20px_rgba(239,68,68,0.3)]' : 'border-border'}`}>
                        <div className="flex items-center gap-2 mb-4">
                          <GeminiLogo className={`w-5 h-5 ${isAdvancedThreat ? 'text-danger animate-pulse' : ''}`} />
                          <h3 className="text-white font-bold flex items-center gap-2">
                            Análisis Inteligente
                            <div className="relative group flex items-center justify-center">
                              <Info className="w-4 h-4 text-gray-500 hover:text-primary transition-colors cursor-help" />
                              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-64 bg-surface border border-border text-gray-300 text-xs rounded-lg p-3 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none text-center">
                                Motor analítico impulsado por Gemini 2.5 Flash. Es capaz de leer contexto, intenciones y engaños visuales (Zero-Day) en archivos y URLs.
                                <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-surface drop-shadow-lg"></div>
                              </div>
                            </div>
                            {isAdvancedThreat && (
                              <span className="text-[11px] bg-danger/20 text-danger border border-danger/40 px-3 py-1 rounded-full font-black tracking-wider uppercase flex items-center gap-1">
                                <ShieldAlert className="w-3 h-3" /> NO ABRIR: PHISHING DETECTADO POR IA
                              </span>
                            )}
                          </h3>
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

                        {
                          analysisResult.engines?.map((engine, idx) => (
                            <motion.div
                              key={idx}
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: idx * 0.1 }}
                              className="bg-background rounded-lg p-4 border border-border flex items-center justify-between group hover:border-primary/50 transition-colors"
                            >
                              <div className="flex items-center gap-3 flex-1">
                                {engine.name === 'VirusTotal' ? <VirusTotalLogo className="w-8 h-8" /> :
                                  engine.name === 'MetaDefender' ? <MetaDefenderLogo className="w-8 h-8" /> :
                                    <Shield className="w-8 h-8 text-gray-600" />}

                                <div className="flex-1 ml-3"> {/* Added flex-1 and ml-3 for spacing */}
                                  <div className="flex justify-between items-start mb-1 gap-4"> {/* Changed items-center to items-start for multiline text */}
                                    <span className="text-white font-medium shrink-0 flex items-center gap-1.5 z-10">
                                      {engine.name}
                                      {engine.name === 'Clasificador Heurístico' && (
                                        <div className="relative group flex items-center justify-center">
                                          <Info className="w-3.5 h-3.5 text-gray-600 hover:text-primary transition-colors cursor-help" />
                                          <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-64 bg-surface border border-border text-gray-300 text-xs rounded-lg p-3 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none text-center font-normal">
                                            Algoritmo de Machine Learning local diseñado para detectar patrones anómalos en URLs basado en características como longitud, caracteres especiales y entropía.
                                            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-surface drop-shadow-lg"></div>
                                          </div>
                                        </div>
                                      )}
                                    </span>

                                    <div className="flex items-center gap-2 flex-1 justify-end min-w-0">
                                      <span className={`text-sm font-bold text-right break-words whitespace-normal leading-tight ${engine.detected || (engine.positives && engine.positives > 0) ? 'text-danger' :
                                        engine.warning ? 'text-warning' : 'text-success'}`}>
                                        {engine.status_text ? engine.status_text :
                                          (engine.detected || (engine.positives && engine.positives > 0) ? 'Amenaza Detectada' :
                                            engine.warning ? 'Precaución' : 'Limpio')}
                                      </span>

                                      {engine.link && engine.link !== '#' && !(analysisType === 'url' && engine.name === 'MetaDefender') && (
                                        <a
                                          href={engine.link}
                                          target="_blank"
                                          rel="noreferrer"
                                          className="text-gray-500 hover:text-primary transition-colors flex items-center justify-center p-0.5 shrink-0"
                                        >
                                          <ArrowRight className="w-4 h-4" />
                                        </a>
                                      )}
                                    </div>
                                  </div>
                                  {/* Show x/x for engines that support it */}
                                  {(engine.total > 0) && (
                                    <p className="text-xs text-gray-500 mt-0.5">
                                      {engine.positives}/{engine.total} motores
                                    </p>
                                  )}
                                </div>
                              </div>
                            </motion.div>
                          ))
                        }
                      </div>
                    </>
                  );
                })()}
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div >

      {/* SUCCESS TOAST NOTIFICATION */}
      < AnimatePresence >
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: -50, x: '-50%' }}
            className="fixed top-8 left-1/2 z-50 flex items-center gap-4 bg-success/10 border border-success text-success px-6 py-4 rounded-xl shadow-2xl backdrop-blur-md"
          >
            <div className="bg-success rounded-full p-1">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="font-bold text-lg">¡Reporte Enviado!</h4>
              <p className="text-sm opacity-90">El incidente ha sido registrado exitosamente.</p>
            </div>
            <button onClick={() => setShowSuccess(false)} className="ml-4 hover:bg-success/20 p-1 rounded-lg transition-colors">
              <X className="w-5 h-5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence >

      {/* ERROR TOAST NOTIFICATION */}
      < AnimatePresence >
        {showError && (
          <motion.div
            initial={{ opacity: 0, y: -50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: -50, x: '-50%' }}
            className="fixed top-8 left-1/2 z-50 flex items-center gap-4 bg-danger/10 border border-danger text-danger px-6 py-4 rounded-xl shadow-2xl backdrop-blur-md"
          >
            <div className="bg-danger rounded-full p-1">
              <X className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="font-bold text-lg">Error al Enviar</h4>
              <p className="text-sm opacity-90">Hubo un problema al registrar el incidente.</p>
            </div>
            <button onClick={() => setShowError(false)} className="ml-4 hover:bg-danger/20 p-1 rounded-lg transition-colors">
              <X className="w-5 h-5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence >

    </div >
  );
};

export default EmployeeDashboard;
