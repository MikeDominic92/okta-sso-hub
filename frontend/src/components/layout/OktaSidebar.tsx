'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { LayoutGrid, Grid, Globe, Shield, Users, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutGrid },
    { name: 'Applications', href: '/apps', icon: Grid },
    { name: 'Federation', href: '/federation', icon: Globe },
    { name: 'Security', href: '/security', icon: Shield },
    { name: 'Provisioning', href: '/provisioning', icon: Users },
];

export function OktaSidebar() {
    const pathname = usePathname();

    return (
        <div className="w-64 border-r border-white/5 bg-obsidian-black h-screen fixed left-0 top-0 flex flex-col z-50">
            <div className="p-6 flex items-center gap-3 border-b border-white/5">
                <div className="w-8 h-8 rounded-full bg-okta-blue flex items-center justify-center shadow-blue-glow">
                    <span className="font-bold text-white text-lg">O</span>
                </div>
                <span className="font-bold text-xl text-ghost-white tracking-tight">Okta Hub</span>
            </div>

            <nav className="flex-1 p-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group relative overflow-hidden",
                                isActive
                                    ? "bg-okta-blue/10 text-electric-cyan"
                                    : "text-slate-gray hover:text-ghost-white hover:bg-white/5"
                            )}
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="activeNav"
                                    className="absolute left-0 top-0 bottom-0 w-1 bg-electric-cyan shadow-[0_0_10px_rgba(0,212,255,0.5)]"
                                />
                            )}
                            <item.icon className={cn("w-4 h-4 transition-colors", isActive ? "text-electric-cyan" : "group-hover:text-ghost-white")} />
                            <span className="font-medium text-sm">{item.name}</span>
                            {isActive && <ChevronRight className="w-4 h-4 ml-auto text-electric-cyan/50" />}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-white/5">
                <div className="p-4 rounded-xl bg-gradient-to-br from-dark-surface to-black border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 rounded-full bg-success-green animate-pulse" />
                        <span className="text-xs font-medium text-success-green">System Operational</span>
                    </div>
                    <p className="text-xs text-slate-gray font-mono">v2024.12.1</p>
                </div>
            </div>
        </div>
    );
}
