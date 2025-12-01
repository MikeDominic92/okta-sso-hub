'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { User, Shield, Server, CheckCircle } from 'lucide-react';

export function FlowDiagram() {
    return (
        <div className="relative h-48 w-full flex items-center justify-between px-8 bg-black/20 rounded-xl border border-white/5 overflow-hidden">
            {/* Background Grid */}
            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />

            {/* User */}
            <div className="relative z-10 flex flex-col items-center gap-2">
                <div className="w-12 h-12 rounded-full bg-white/10 border border-white/20 flex items-center justify-center">
                    <User className="w-6 h-6 text-ghost-white" />
                </div>
                <span className="text-xs font-mono text-slate-gray">User</span>
            </div>

            {/* Flow Line 1 */}
            <div className="flex-1 h-px bg-white/10 relative mx-4">
                <motion.div
                    animate={{ x: ['0%', '100%'], opacity: [0, 1, 0] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="absolute top-1/2 -translate-y-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-electric-cyan to-transparent"
                />
            </div>

            {/* Okta */}
            <div className="relative z-10 flex flex-col items-center gap-2">
                <div className="w-16 h-16 rounded-2xl bg-okta-blue/20 border border-okta-blue/50 flex items-center justify-center shadow-blue-glow">
                    <div className="w-10 h-10 rounded-full bg-okta-blue flex items-center justify-center">
                        <span className="font-bold text-white">O</span>
                    </div>
                </div>
                <span className="text-xs font-mono text-okta-blue font-bold">Okta</span>
            </div>

            {/* Flow Line 2 */}
            <div className="flex-1 h-px bg-white/10 relative mx-4">
                <motion.div
                    animate={{ x: ['0%', '100%'], opacity: [0, 1, 0] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: 1 }}
                    className="absolute top-1/2 -translate-y-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-success-green to-transparent"
                />
            </div>

            {/* App */}
            <div className="relative z-10 flex flex-col items-center gap-2">
                <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center">
                    <Server className="w-6 h-6 text-ghost-white" />
                </div>
                <span className="text-xs font-mono text-slate-gray">App</span>
            </div>

            {/* Success Indicator */}
            <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: [0, 1.2, 1], opacity: [0, 1, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: 1.8 }}
                className="absolute right-10 top-10"
            >
                <CheckCircle className="w-6 h-6 text-success-green" />
            </motion.div>
        </div>
    );
}
