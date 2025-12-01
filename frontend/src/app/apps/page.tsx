'use client';

import React, { useState } from 'react';
import { OktaShell } from '@/components/layout/OktaShell';
import { SSOCard } from '@/components/ui/SSOCard';
import { AppBadge } from '@/components/ui/AppBadge';
import { Search, Plus, Filter, MoreHorizontal, Users, Settings, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const apps = [
    { id: 1, name: 'Salesforce', category: 'CRM', protocol: 'saml', status: 'active', users: 1250, logo: 'S' },
    { id: 2, name: 'Slack', category: 'Collaboration', protocol: 'oidc', status: 'active', users: 3400, logo: 'Sl' },
    { id: 3, name: 'Workday', category: 'HR', protocol: 'saml', status: 'active', users: 3400, logo: 'W' },
    { id: 4, name: 'AWS SSO', category: 'Infrastructure', protocol: 'saml', status: 'active', users: 150, logo: 'A' },
    { id: 5, name: 'Zoom', category: 'Collaboration', protocol: 'oidc', status: 'pending', users: 0, logo: 'Z' },
    { id: 6, name: 'Jira', category: 'DevOps', protocol: 'saml', status: 'active', users: 800, logo: 'J' },
    { id: 7, name: 'GitHub Enterprise', category: 'DevOps', protocol: 'oidc', status: 'active', users: 450, logo: 'G' },
    { id: 8, name: 'ServiceNow', category: 'ITSM', protocol: 'saml', status: 'error', users: 120, logo: 'Sn' },
];

export default function AppCatalog() {
    const [isWizardOpen, setIsWizardOpen] = useState(false);
    const [filter, setFilter] = useState('all');

    return (
        <OktaShell>
            <div className="space-y-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-ghost-white mb-2">Application Catalog</h1>
                        <p className="text-slate-gray">Manage integrated applications and SSO configurations.</p>
                    </div>
                    <button
                        onClick={() => setIsWizardOpen(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-okta-blue hover:bg-electric-cyan text-white font-bold rounded-lg transition-all shadow-blue-glow hover:shadow-cyan-glow"
                    >
                        <Plus className="w-4 h-4" />
                        <span>Add Integration</span>
                    </button>
                </div>

                {/* Filters & Search */}
                <div className="flex items-center gap-4 bg-white/5 p-2 rounded-xl border border-white/5">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-gray" />
                        <input
                            type="text"
                            placeholder="Search applications..."
                            className="w-full bg-transparent border-none focus:ring-0 text-ghost-white pl-10 placeholder:text-slate-gray/50"
                        />
                    </div>
                    <div className="h-6 w-px bg-white/10" />
                    <div className="flex gap-2">
                        {['all', 'active', 'pending', 'error'].map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize ${filter === f
                                        ? 'bg-white/10 text-ghost-white'
                                        : 'text-slate-gray hover:text-ghost-white hover:bg-white/5'
                                    }`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>
                </div>

                {/* App Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {apps.map((app) => (
                        <SSOCard key={app.id} className="group cursor-pointer">
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 flex items-center justify-center font-bold text-xl text-ghost-white">
                                    {app.logo}
                                </div>
                                <button className="p-1 rounded-lg hover:bg-white/10 text-slate-gray hover:text-ghost-white transition-colors">
                                    <MoreHorizontal className="w-5 h-5" />
                                </button>
                            </div>

                            <h3 className="text-lg font-bold text-ghost-white mb-1">{app.name}</h3>
                            <p className="text-xs text-slate-gray mb-4">{app.category}</p>

                            <div className="flex items-center justify-between mb-4">
                                <AppBadge status={app.status as any} protocol={app.protocol as any} />
                            </div>

                            <div className="pt-4 border-t border-white/5 flex items-center justify-between text-sm text-slate-gray">
                                <div className="flex items-center gap-1.5">
                                    <Users className="w-4 h-4" />
                                    <span>{app.users}</span>
                                </div>
                                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button className="p-1.5 hover:text-electric-cyan transition-colors" title="Settings">
                                        <Settings className="w-4 h-4" />
                                    </button>
                                    <button className="p-1.5 hover:text-electric-cyan transition-colors" title="Launch">
                                        <ExternalLink className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </SSOCard>
                    ))}
                </div>

                {/* Quick Add Wizard Modal */}
                <AnimatePresence>
                    {isWizardOpen && (
                        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                            <motion.div
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.9, opacity: 0 }}
                                className="w-full max-w-2xl bg-dark-surface border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                            >
                                <div className="p-6 border-b border-white/10 flex items-center justify-between">
                                    <h2 className="text-xl font-bold text-ghost-white">Add Integration</h2>
                                    <button
                                        onClick={() => setIsWizardOpen(false)}
                                        className="text-slate-gray hover:text-ghost-white"
                                    >
                                        ✕
                                    </button>
                                </div>
                                <div className="p-8">
                                    <div className="grid grid-cols-3 gap-4 mb-8">
                                        {['Browse Catalog', 'Configure SSO', 'Assign Users'].map((step, i) => (
                                            <div key={step} className="flex flex-col items-center gap-2 relative">
                                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border ${i === 0 ? 'bg-okta-blue border-okta-blue text-white' : 'bg-transparent border-white/20 text-slate-gray'
                                                    }`}>
                                                    {i + 1}
                                                </div>
                                                <span className={`text-xs font-medium ${i === 0 ? 'text-ghost-white' : 'text-slate-gray'}`}>{step}</span>
                                                {i < 2 && <div className="absolute top-4 left-1/2 w-full h-px bg-white/10 -z-10" />}
                                            </div>
                                        ))}
                                    </div>

                                    <div className="space-y-4">
                                        <h3 className="text-lg font-bold text-ghost-white">Popular Integrations</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            {['Office 365', 'Google Workspace', 'Box', 'Zendesk'].map((app) => (
                                                <button key={app} className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/5 hover:border-okta-blue/50 hover:bg-okta-blue/5 transition-all text-left group">
                                                    <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center font-bold text-ghost-white">
                                                        {app[0]}
                                                    </div>
                                                    <div>
                                                        <p className="font-bold text-ghost-white group-hover:text-electric-cyan transition-colors">{app}</p>
                                                        <p className="text-xs text-slate-gray">SAML 2.0 • OIDC</p>
                                                    </div>
                                                    <Plus className="w-5 h-5 ml-auto text-slate-gray group-hover:text-electric-cyan opacity-0 group-hover:opacity-100 transition-all" />
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                <div className="p-6 border-t border-white/10 bg-black/20 flex justify-end gap-3">
                                    <button
                                        onClick={() => setIsWizardOpen(false)}
                                        className="px-4 py-2 rounded-lg text-slate-gray hover:text-ghost-white hover:bg-white/5 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button className="px-4 py-2 bg-white/10 text-slate-gray cursor-not-allowed rounded-lg font-medium">
                                        Next Step
                                    </button>
                                </div>
                            </motion.div>
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </OktaShell>
    );
}
