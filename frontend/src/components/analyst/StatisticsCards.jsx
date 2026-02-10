import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Clock, Activity, CheckCircle, ShieldAlert, FileText, Link } from 'lucide-react';

const COLORS = {
    'CRITICAL': '#EF4444',
    'HIGH': '#F97316',
    'MEDIUM': '#EAB308',
    'LOW': '#3B82F6',
    'SAFE': '#22C55E',
    'UNKNOWN': '#9CA3AF'
};

const PIE_COLORS = ['#3B82F6', '#22C55E'];

const StatisticsCards = ({ stats }) => {
    if (!stats) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

            {/* Card 1: Tipos */}
            <div className="bg-surface p-6 rounded-xl border border-border">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider">Incidentes por Tipo</h3>
                    <div className="flex gap-2">
                        <FileText className="w-4 h-4 text-blue-400" />
                        <Link className="w-4 h-4 text-green-400" />
                    </div>
                </div>
                <div className="h-40">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={[
                                    { name: 'Archivos', value: stats.by_type.files },
                                    { name: 'URLs', value: stats.by_type.urls }
                                ]}
                                cx="50%" cy="50%" innerRadius={40} outerRadius={60}
                                paddingAngle={5} dataKey="value"
                            >
                                {PIE_COLORS.map((color, index) => (
                                    <Cell key={`cell-${index}`} fill={color} />
                                ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Card 2: Riesgo */}
            <div className="bg-surface p-6 rounded-xl border border-border">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider">Por Nivel de Riesgo</h3>
                    <ShieldAlert className="w-4 h-4 text-red-400" />
                </div>
                <div className="h-40">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            layout="vertical"
                            data={[
                                { name: 'CRITICO', value: stats.by_risk.CRITICAL, fill: COLORS.CRITICAL },
                                { name: 'ALTO', value: stats.by_risk.HIGH, fill: COLORS.HIGH },
                                { name: 'MEDIO', value: stats.by_risk.MEDIUM, fill: COLORS.MEDIUM },
                                { name: 'BAJO', value: stats.by_risk.LOW, fill: COLORS.LOW },
                            ]}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                            <XAxis type="number" hide />
                            <YAxis dataKey="name" type="category" width={60} tick={{ fill: '#9CA3AF', fontSize: 10, fontWeight: 'bold' }} />
                            <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                                {
                                    [
                                        { fill: COLORS.CRITICAL },
                                        { fill: COLORS.HIGH },
                                        { fill: COLORS.MEDIUM },
                                        { fill: COLORS.LOW },
                                    ].map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))
                                }
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Card 3: Estado */}
            <div className="bg-surface p-6 rounded-xl border border-border">
                <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-6">Estado de Gestión</h3>
                <div className="grid grid-cols-3 gap-4">
                    <div className="flex flex-col items-center p-3 bg-background rounded-lg border border-border">
                        <Clock className="w-6 h-6 text-gray-400 mb-2" />
                        <div className="text-2xl font-bold text-white">{stats.by_status.pending}</div>
                        <div className="text-[10px] text-gray-500 uppercase font-bold">Pendientes</div>
                    </div>
                    <div className="flex flex-col items-center p-3 bg-background rounded-lg border border-border">
                        <Activity className="w-6 h-6 text-yellow-500 mb-2" />
                        <div className="text-2xl font-bold text-white">{stats.by_status.investigating}</div>
                        <div className="text-[10px] text-gray-500 uppercase font-bold">Revisión</div>
                    </div>
                    <div className="flex flex-col items-center p-3 bg-background rounded-lg border border-border">
                        <CheckCircle className="w-6 h-6 text-green-500 mb-2" />
                        <div className="text-2xl font-bold text-white">{stats.by_status.resolved}</div>
                        <div className="text-[10px] text-gray-500 uppercase font-bold">Resueltos</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StatisticsCards;
