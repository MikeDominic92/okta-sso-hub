'use client';

import React from 'react';
import { OktaShell } from '@/components/layout/OktaShell';
import { SSOCard } from '@/components/ui/SSOCard';
import { Users, RefreshCw, UserMinus, UserPlus, ArrowRight, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

const events = [
    { id: 1, type: 'create', user: 'alice.smith@corp.com', app: 'Salesforce', status: 'success', time: '2m ago' },
    { id: 2, type: 'update', user: 'bob.jones@corp.com', app: 'Slack', status: 'success', time: '15m ago' },
    { id: 3, type: 'delete', user: 'charlie.brown@corp.com', app: 'Zoom', status: 'failed', time: '1h ago' },
    { id: 4, type: 'create', user: 'david.lee@corp.com', app: 'Jira', status: 'success', time: '2h ago' },
    { id: 5, type: 'update', user: 'eve.white@corp.com', app: 'Workday', status: 'success', time: '3h ago' },
];

export default function Provisioning() {
    return (
        <OktaShell>
            <div className="space-y-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-ghost-white mb-2">User Lifecycle & Provisioning</h1>
                        <p className="text-slate-gray">Monitor SCIM events and automated user management.</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-okta-blue/10 border border-okta-blue/20">
                            <RefreshCw className="w-4 h-4 text-okta-blue animate-spin-slow" />
                            <span className="text-xs font-medium text-okta-blue">Sync Active</span>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Stats */}
                    <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-4 gap-6">
                        <SSOCard>
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-okta-blue/10 border border-okta-blue/20">
                                    <Users className="w-6 h-6 text-okta-blue" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Total Users</p>
                                    <p className="text-2xl font-bold text-ghost-white">12,450</p>
                                </div>
                            </div>
                        </SSOCard>
                        <SSOCard>
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-success-green/10 border border-success-green/20">
                                    <UserPlus className="w-6 h-6 text-success-green" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Provisioned (24h)</p>
                                    <p className="text-2xl font-bold text-ghost-white">145</p>
                                </div>
                            </div>
                        </SSOCard>
                        <SSOCard>
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-warning-amber/10 border border-warning-amber/20">
                                    <UserMinus className="w-6 h-6 text-warning-amber" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Deprovisioned (24h)</p>
                                    <p className="text-2xl font-bold text-ghost-white">23</p>
                                </div>
                            </div>
                        </SSOCard>
                        <SSOCard>
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-xl bg-error-red/10 border border-error-red/20">
                                    <XCircle className="w-6 h-6 text-error-red" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Sync Errors</p>
                                    <p className="text-2xl font-bold text-ghost-white">5</p>
                                </div>
                            </div>
                        </SSOCard>
                    </div>

                    {/* Timeline */}
                    <div className="lg:col-span-2 space-y-6">
                        <SSOCard title="Provisioning Timeline" icon={Clock}>
                            <div className="space-y-6 relative">
                                <div className="absolute left-6 top-4 bottom-4 w-px bg-white/10" />

                                {events.map((event) => (
                                    <div key={event.id} className="relative flex items-start gap-6 group">
                                        <div className={cn(
                                            "w-12 h-12 rounded-full border-4 border-obsidian-black flex items-center justify-center shrink-0 z-10",
                                            event.status === 'success' ? "bg-success-green/20 text-success-green" : "bg-error-red/20 text-error-red"
                                        )}>
                                            {event.type === 'create' ? <UserPlus className="w-5 h-5" /> :
                                                event.type === 'delete' ? <UserMinus className="w-5 h-5" /> :
                                                    <RefreshCw className="w-5 h-5" />}
                                        </div>

                                        <div className="flex-1 p-4 rounded-xl bg-white/5 border border-white/5 group-hover:border-okta-blue/30 transition-colors">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    <span className={cn(
                                                        "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                                                        event.type === 'create' ? "bg-success-green/10 text-success-green" :
                                                            event.type === 'delete' ? "bg-error-red/10 text-error-red" :
                                                                "bg-okta-blue/10 text-okta-blue"
                                                    )}>
                                                        {event.type}
                                                    </span>
                                                    <span className="text-xs text-slate-gray">{event.time}</span>
                                                </div>
                                                {event.status === 'failed' && (
                                                    <span className="text-xs text-error-red font-bold flex items-center gap-1">
                                                        <AlertTriangle className="w-3 h-3" /> Failed
                                                    </span>
                                                )}
                                            </div>

                                            <div className="flex items-center gap-3 text-sm">
                                                <span className="font-bold text-ghost-white">{event.user}</span>
                                                <ArrowRight className="w-4 h-4 text-slate-gray" />
                                                <span className="font-bold text-electric-cyan">{event.app}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </SSOCard>
                    </div>

                    {/* Deprovisioning Tracker */}
                    <div className="lg:col-span-1 space-y-6">
                        <SSOCard title="Pending Deprovisioning" icon={UserMinus}>
                            <div className="space-y-4">
                                {[
                                    { user: 'john.doe@corp.com', date: 'Today', days: 0 },
                                    { user: 'jane.smith@corp.com', date: 'Tomorrow', days: 1 },
                                    { user: 'mike.williams@corp.com', date: 'Dec 05', days: 3 },
                                ].map((item) => (
                                    <div key={item.user} className="p-3 rounded-lg bg-warning-amber/5 border border-warning-amber/10 flex items-center justify-between">
                                        <div>
                                            <p className="text-sm font-bold text-ghost-white">{item.user}</p>
                                            <p className="text-xs text-slate-gray">Scheduled: {item.date}</p>
                                        </div>
                                        <div className="text-center px-3 py-1 rounded bg-black/20">
                                            <p className="text-xs font-bold text-warning-amber">{item.days}d</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <button className="w-full mt-4 py-2 bg-error-red/10 hover:bg-error-red/20 text-error-red border border-error-red/20 rounded-lg transition-colors text-sm font-bold">
                                Process All Now
                            </button>
                        </SSOCard>

                        <SSOCard title="Group Push Status" icon={Users}>
                            <div className="space-y-3">
                                {[
                                    { group: 'Engineering', app: 'GitHub', status: 'synced' },
                                    { group: 'Sales', app: 'Salesforce', status: 'synced' },
                                    { group: 'Marketing', app: 'Slack', status: 'pending' },
                                ].map((push) => (
                                    <div key={push.group} className="flex items-center justify-between p-2 rounded hover:bg-white/5 transition-colors">
                                        <div>
                                            <p className="text-sm font-medium text-ghost-white">{push.group}</p>
                                            <p className="text-xs text-slate-gray">to {push.app}</p>
                                        </div>
                                        {push.status === 'synced' ? (
                                            <CheckCircle className="w-4 h-4 text-success-green" />
                                        ) : (
                                            <RefreshCw className="w-4 h-4 text-warning-amber animate-spin" />
                                        )}
                                    </div>
                                ))}
                            </div>
                        </SSOCard>
                    </div>
                </div>
            </div>
        </OktaShell>
    );
}
