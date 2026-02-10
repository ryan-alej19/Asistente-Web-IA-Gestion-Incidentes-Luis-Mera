import React, { useState } from 'react';
import axios from 'axios';
import { Icons } from './Icons';
import API_URL from '../config/api';

/**
 * Botones de exportación (CSV / PDF) para RF-06
 */
const ExportButtons = () => {
    const [downloading, setDownloading] = useState(false);

    const handleDownload = async (format) => {
        try {
            setDownloading(true);
            const token = localStorage.getItem('access_token');
            const url = `${API_URL}/api/incidents/export/${format}/`;

            const response = await axios.get(url, {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob', // Importante para descargas
            });

            // Crear link temporal
            const href = window.URL.createObjectURL(response.data);
            const link = document.createElement('a');
            link.href = href;
            link.setAttribute('download', `reporte_incidentes.${format}`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(href);

            setDownloading(false);
        } catch (err) {
            console.error("Error downloading report:", err);
            alert("Error al descargar reporte. Intente nuevamente.");
            setDownloading(false);
        }
    };

    return (
        <div className="absolute top-4 right-4 flex gap-3">
            <button
                onClick={() => handleDownload('csv')}
                disabled={downloading}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-semibold shadow-md transition-all hover:opacity-90 disabled:opacity-50"
                title="Exportar CSV"
            >
                <Icons.ChartBar className="h-5 w-5" />
                <span className="hidden sm:inline">CSV</span>
            </button>
            <button
                onClick={() => handleDownload('pdf')}
                disabled={downloading}
                className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md font-semibold shadow-md transition-all hover:opacity-90 disabled:opacity-50"
                title="Exportar PDF"
            >
                <Icons.File className="h-5 w-5" />
                <span className="hidden sm:inline">PDF</span>
            </button>
        </div>
    );
};

export default ExportButtons;
