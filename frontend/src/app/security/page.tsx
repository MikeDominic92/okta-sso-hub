'use client';

import React from 'react';
import { OktaShell } from '@/components/layout/OktaShell';
import { SSOCard } from '@/components/ui/SSOCard';
import { PolicyRule } from '@/components/ui/PolicyRule';
import { Shield, Smartphone, Lock, AlertTriangle, Plus, Fingerprint, Mail, Key } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const riskData = [
    { name: 'Low', value: 850, color: '#10B981' },
    { name: 'Medium', value: 120, color: '#F59E0B' },
    { name: 'High', value: 45, color: '#EF4444' },
];

export default function Security() {
    return (
        <OktaShell>
            <div className="space-y-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-ghost-white mb-2">MFA & Security Policies</h1>
                        <p className="text-slate-gray">Configure adaptive authentication and sign-on rules.</p>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 bg-okta-blue hover:bg-electric-cyan text-white font-bold rounded-lg transition-all shadow-blue-glow">
                        <Plus className="w-4 h-4" />
                        <span>Add Policy</span>
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Factor Enrollment */}
                    <div className="lg:col-span-1 space-y-6">
                        <SSOCard title="MFA Enrollment" icon={Smartphone}>
                            <div className="space-y-4">
                                {[
                                    { name: 'Okta Verify', count: '98%', icon: Shield, status: 'required' },
                                    { name: 'WebAuthn / FIDO2', count: '45%', icon: Fingerprint, status: 'optional' },
                                    { name: 'Email Magic Link', count: '100%', icon: Mail, status: 'recovery' },
                                ].map((factor) => (
                                    <div key={factor.name} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 rounded-lg bg-black/20">
                                                <factor.icon className="w-4 h-4 text-electric-cyan" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-ghost-white">{factor.name}</p>
                                                <p className="text-xs text-slate-gray capitalize">{factor.status}</p>
                                            </div>
                                        </div>
                                        <span className="text-lg font-bold text-ghost-white">{factor.count}</span>
                                    </div>
                                ))}
                            </div>
                        </SSOCard>

                        <SSOCard title="Risk Scoring" icon={AlertTriangle}>
                            <div className="h-48">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={riskData} layout="vertical">
                                        <XAxis type="number" hide />
                                        <YAxis dataKey="name" type="category" width={60} tick={{ fill: '#94A3B8', fontSize: 12 }} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            cursor={{ fill: 'transparent' }}
                                            contentStyle={{ backgroundColor: '#18181B', borderColor: '#333', borderRadius: '8px' }}
                                        />
                                        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                                            {riskData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="mt-4 p-3 rounded-lg bg-warning-amber/10 border border-warning-amber/20 flex items-start gap-3">
                                <AlertTriangle className="w-5 h-5 text-warning-amber shrink-0" />
                                <div>
                                    <p className="text-sm font-bold text-warning-amber">Adaptive MFA Active</p>
                                    <p className="text-xs text-slate-gray mt-1">High-risk logins from new devices will trigger biometric challenge.</p>
                                </div>
                            </div>
                        </SSOCard>
                    </div>

                    {/* Policy Builder */}
                    <div className="lg:col-span-2 space-y-6">
                        <SSOCard title="Global Sign-On Policy" icon={Lock}>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 bg-okta-blue/10 border border-okta-blue/30 rounded-xl">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-full bg-okta-blue flex items-center justify-center font-bold text-white">1</div>
                                        <div>
                                            <h3 className="font-bold text-ghost-white">Default Rule</h3>
                                            <p className="text-sm text-slate-gray">Applies to all users</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="text-sm text-slate-gray">Priority: Lowest</span>
                                        <button className="text-electric-cyan hover:text-white text-sm font-bold">Edit</button>
                                    </div>
                                </div>

                                <div className="relative pl-8 space-y-4 border-l-2 border-white/10 ml-5">
                                    <PolicyRule
                                        name="Admins - High Assurance"
                                        conditions={{ network: 'Any', device: 'Managed', risk: 'Any' }}
                                        action="mfa"
                                    />
                                    <PolicyRule
                                        name="Contractors - Restricted"
                                        conditions={{ network: 'Off-Network', device: 'Unmanaged', risk: 'Medium+' }}
                                        action="deny"
                                    />
                                    <PolicyRule
                                        name="Employees - Standard"
                                        conditions={{ network: 'Corporate-VPN', device: 'Any', risk: 'Low' }}
                                        action="allow"
                                    />
                                </div>
                            </div>
                        </SSOCard>

                        <SSOCard title="Password Policy" icon={Key}>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Min Length</p>
                                    <p className="text-xl font-bold text-ghost-white">12 Characters</p>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Complexity</p>
                                    <p className="text-xl font-bold text-ghost-white">High (A-z, 0-9, !@#)</p>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">History</p>
                                    <p className="text-xl font-bold text-ghost-white">Last 5 Passwords</p>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Expiry</p>
                                    <p className="text-xl font-bold text-ghost-white">90 Days</p>
                                </div>
                            </div>
                        </SSOCard>
                    </div>
                </div>
            </div>
        </OktaShell>
    );
}
