'use client';

import React, { useState } from 'react';
import { OktaShell } from '@/components/layout/OktaShell';
import { SSOCard } from '@/components/ui/SSOCard';
import { Globe, Shield, CheckCircle, AlertTriangle, RefreshCw, Link, FileCode, Key } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Federation() {
    const [activeIdP, setActiveIdP] = useState('azure-ad');

    return (
        <OktaShell>
            <div className="space-y-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-ghost-white mb-2">Identity Provider Federation</h1>
                        <p className="text-slate-gray">Manage inbound federation and trust relationships.</p>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-ghost-white border border-white/10 rounded-lg transition-colors">
                        <RefreshCw className="w-4 h-4" />
                        <span>Sync Metadata</span>
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* IdP List */}
                    <div className="lg:col-span-4 space-y-4">
                        {[
                            { id: 'azure-ad', name: 'Azure AD (Entra ID)', status: 'active', type: 'SAML 2.0' },
                            { id: 'google', name: 'Google Workspace', status: 'active', type: 'OIDC' },
                            { id: 'adfs', name: 'On-Prem ADFS', status: 'warning', type: 'WS-Fed' },
                        ].map((idp) => (
                            <div
                                key={idp.id}
                                onClick={() => setActiveIdP(idp.id)}
                                className={`p-4 rounded-xl border cursor-pointer transition-all ${activeIdP === idp.id
                                        ? 'bg-okta-blue/10 border-okta-blue/50 shadow-blue-glow'
                                        : 'bg-white/5 border-white/5 hover:bg-white/10'
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className={`font-bold ${activeIdP === idp.id ? 'text-electric-cyan' : 'text-ghost-white'}`}>{idp.name}</h3>
                                    {idp.status === 'active' ? (
                                        <CheckCircle className="w-4 h-4 text-success-green" />
                                    ) : (
                                        <AlertTriangle className="w-4 h-4 text-warning-amber" />
                                    )}
                                </div>
                                <div className="flex items-center gap-2 text-xs text-slate-gray">
                                    <span className="px-2 py-0.5 rounded bg-black/20 border border-white/10">{idp.type}</span>
                                    <span>Last sync: 10m ago</span>
                                </div>
                            </div>
                        ))}

                        <button className="w-full py-3 border border-dashed border-white/20 rounded-xl text-slate-gray hover:text-ghost-white hover:border-white/40 transition-colors flex items-center justify-center gap-2">
                            <PlusIcon />
                            <span>Add Identity Provider</span>
                        </button>
                    </div>

                    {/* Configuration Panel */}
                    <div className="lg:col-span-8 space-y-6">
                        <SSOCard title="Trust Relationship" icon={Shield}>
                            <div className="relative h-40 bg-black/20 rounded-xl border border-white/5 flex items-center justify-center overflow-hidden">
                                <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />

                                <div className="flex items-center gap-8 relative z-10">
                                    <div className="flex flex-col items-center gap-2">
                                        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                                            <Globe className="w-8 h-8 text-ghost-white" />
                                        </div>
                                        <span className="text-sm font-bold text-ghost-white">Azure AD</span>
                                    </div>

                                    <div className="flex flex-col items-center gap-1">
                                        <div className="flex items-center gap-1">
                                            <div className="w-2 h-2 rounded-full bg-success-green animate-pulse" />
                                            <span className="text-xs font-bold text-success-green uppercase tracking-wider">Trusted</span>
                                        </div>
                                        <div className="w-32 h-1 bg-gradient-to-r from-transparent via-success-green to-transparent" />
                                        <Link className="w-4 h-4 text-slate-gray" />
                                    </div>

                                    <div className="flex flex-col items-center gap-2">
                                        <div className="w-16 h-16 rounded-2xl bg-okta-blue/20 border border-okta-blue/50 flex items-center justify-center shadow-blue-glow">
                                            <div className="w-10 h-10 rounded-full bg-okta-blue flex items-center justify-center">
                                                <span className="font-bold text-white">O</span>
                                            </div>
                                        </div>
                                        <span className="text-sm font-bold text-electric-cyan">Okta Hub</span>
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-6 mt-6">
                                <div>
                                    <label className="block text-xs font-medium text-slate-gray uppercase tracking-wider mb-2">Metadata URL</label>
                                    <div className="flex items-center gap-2 bg-black/40 border border-white/10 rounded-lg px-3 py-2">
                                        <Globe className="w-4 h-4 text-slate-gray" />
                                        <span className="text-sm font-mono text-ghost-white truncate">https://login.microsoftonline.com/.../federationmetadata.xml</span>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-slate-gray uppercase tracking-wider mb-2">Entity ID</label>
                                    <div className="flex items-center gap-2 bg-black/40 border border-white/10 rounded-lg px-3 py-2">
                                        <Shield className="w-4 h-4 text-slate-gray" />
                                        <span className="text-sm font-mono text-ghost-white truncate">urn:federation:MicrosoftOnline</span>
                                    </div>
                                </div>
                            </div>
                        </SSOCard>

                        <div className="grid grid-cols-2 gap-6">
                            <SSOCard title="Signing Certificate" icon={Key}>
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between p-3 rounded-lg bg-success-green/5 border border-success-green/10">
                                        <div className="flex items-center gap-3">
                                            <CheckCircle className="w-5 h-5 text-success-green" />
                                            <div>
                                                <p className="text-sm font-bold text-ghost-white">Valid Certificate</p>
                                                <p className="text-xs text-slate-gray">Expires in 245 days</p>
                                            </div>
                                        </div>
                                        <button className="text-xs text-electric-cyan hover:text-white underline">View</button>
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-gray">Thumbprint</span>
                                            <span className="font-mono text-ghost-white">A1:B2:C3...D4</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-gray">Algorithm</span>
                                            <span className="font-mono text-ghost-white">SHA-256</span>
                                        </div>
                                    </div>
                                </div>
                            </SSOCard>

                            <SSOCard title="Attribute Mapping" icon={FileCode}>
                                <div className="space-y-2">
                                    {[
                                        { source: 'userPrincipalName', target: 'login' },
                                        { source: 'givenName', target: 'firstName' },
                                        { source: 'sn', target: 'lastName' },
                                        { source: 'mail', target: 'email' },
                                    ].map((map, i) => (
                                        <div key={i} className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
                                            <span className="font-mono text-xs text-slate-gray">{map.source}</span>
                                            <span className="text-slate-gray">→</span>
                                            <span className="font-mono text-xs text-electric-cyan">{map.target}</span>
                                        </div>
                                    ))}
                                </div>
                                <button className="w-full mt-4 py-2 text-xs font-bold uppercase tracking-wider text-slate-gray hover:text-ghost-white border border-white/10 rounded-lg hover:bg-white/5 transition-colors">
                                    Edit Mappings
                                </button>
                            </SSOCard>
                        </div>
                    </div>
                </div>
            </div>
        </OktaShell>
    );
}

function PlusIcon() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14" />
            <path d="M12 5v14" />
        </svg>
    )
}
