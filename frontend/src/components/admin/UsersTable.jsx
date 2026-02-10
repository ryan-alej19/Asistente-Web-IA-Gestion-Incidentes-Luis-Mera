import React from 'react';
import { motion } from 'framer-motion';
import {
    User, Shield, Activity, MoreHorizontal, UserX, UserCheck,
    Briefcase, Calendar, Clock
} from 'lucide-react';

const UsersTable = ({ users, onToggleStatus, onChangeRole }) => {

    const getRoleBadge = (role) => {
        switch (role) {
            case 'admin': return (
                <span className="flex items-center gap-1.5 bg-yellow-500/10 text-yellow-400 px-2.5 py-1 rounded-lg text-xs font-bold border border-yellow-500/20">
                    <Shield className="w-3 h-3" /> ADMIN
                </span>
            );
            case 'analyst': return (
                <span className="flex items-center gap-1.5 bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-lg text-xs font-bold border border-blue-500/20">
                    <Activity className="w-3 h-3" /> ANALISTA
                </span>
            );
            case 'employee': return (
                <span className="flex items-center gap-1.5 bg-gray-500/10 text-gray-400 px-2.5 py-1 rounded-lg text-xs font-bold border border-gray-500/20">
                    <Briefcase className="w-3 h-3" /> EMPLEADO
                </span>
            );
            default: return <span className="bg-gray-700 text-gray-400 px-2 py-1 rounded text-xs">UNKNOWN</span>;
        }
    };

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.05
            }
        }
    };

    const item = {
        hidden: { opacity: 0, x: -10 },
        show: { opacity: 1, x: 0 }
    };

    return (
        <div className="bg-surface rounded-xl shadow-lg border border-border overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-background/50 border-b border-border text-gray-400 text-xs uppercase tracking-wider font-bold">
                            <th className="p-4 font-semibold">Usuario / Email</th>
                            <th className="p-4 font-semibold">Rol</th>
                            <th className="p-4 font-semibold">Estado</th>
                            <th className="p-4 font-semibold">Registro / Último Acceso</th>
                            <th className="p-4 font-semibold text-right">Acciones</th>
                        </tr>
                    </thead>
                    <motion.tbody
                        variants={container}
                        initial="hidden"
                        animate="show"
                        className="divide-y divide-border"
                    >
                        {users.map((user) => (
                            <motion.tr
                                key={user.id}
                                variants={item}
                                className="hover:bg-white/5 transition-colors group"
                            >
                                <td className="p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xs uppercase">
                                            {user.username[0]}
                                        </div>
                                        <div className="flex flex-col">
                                            <span className="text-white font-medium text-sm">{user.username}</span>
                                            <span className="text-gray-500 text-xs">{user.email || 'Sin email'}</span>
                                        </div>
                                    </div>
                                </td>
                                <td className="p-4">
                                    {getRoleBadge(user.role)}
                                </td>
                                <td className="p-4">
                                    {user.is_active ? (
                                        <span className="inline-flex items-center gap-1.5 text-green-400 text-xs font-bold bg-green-500/10 px-2.5 py-1 rounded-full border border-green-500/20">
                                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> Activo
                                        </span>
                                    ) : (
                                        <span className="inline-flex items-center gap-1.5 text-red-400 text-xs font-bold bg-red-500/10 px-2.5 py-1 rounded-full border border-red-500/20">
                                            <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span> Inactivo
                                        </span>
                                    )}
                                </td>
                                <td className="p-4">
                                    <div className="flex flex-col gap-1">
                                        <span className="text-gray-400 text-xs flex items-center gap-1.5">
                                            <Calendar className="w-3 h-3 text-gray-500" />
                                            Reg: <span className="text-gray-300">{user.date_joined_formatted}</span>
                                        </span>
                                        <span className="text-gray-400 text-xs flex items-center gap-1.5">
                                            <Clock className="w-3 h-3 text-gray-500" />
                                            Login: <span className="text-gray-300">{user.last_login_formatted}</span>
                                        </span>
                                    </div>
                                </td>
                                <td className="p-4 text-right">
                                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">

                                        {/* Change Role Dropdown */}
                                        <div className="relative">
                                            <select
                                                className="bg-background border border-border text-gray-300 text-xs rounded-lg px-2 py-1.5 outline-none focus:border-primary focus:ring-1 focus:ring-primary appearance-none pr-6 cursor-pointer hover:border-gray-500 transition-colors"
                                                value={user.role}
                                                onChange={(e) => onChangeRole(user.id, e.target.value)}
                                                disabled={user.username === 'admin'}
                                            >
                                                <option value="employee">Empleado</option>
                                                <option value="analyst">Analista</option>
                                                <option value="admin">Admin</option>
                                            </select>
                                            <MoreHorizontal className="w-3 h-3 text-gray-500 absolute right-1.5 top-2 pointer-events-none" />
                                        </div>

                                        {/* Toggle Active Button */}
                                        <button
                                            onClick={() => onToggleStatus(user.id)}
                                            className={`p-1.5 rounded-lg transition-all ${user.is_active
                                                ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20'
                                                : 'bg-green-500/10 text-green-400 hover:bg-green-500/20 border border-green-500/20'
                                                }`}
                                            title={user.is_active ? "Desactivar Usuario" : "Activar Usuario"}
                                        >
                                            {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </td>
                            </motion.tr>
                        ))}
                    </motion.tbody>
                </table>
                {users.length === 0 && (
                    <div className="p-12 text-center text-gray-500 flex flex-col items-center">
                        <User className="w-12 h-12 text-gray-600 mb-4 opacity-50" />
                        <p className="text-gray-400 font-medium">No se encontraron usuarios.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default UsersTable;
