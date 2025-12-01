'use client';

import React from 'react';
import { OktaShell } from '@/components/layout/OktaShell';
import { SSOCard } from '@/components/ui/SSOCard';
import { FlowDiagram } from '@/components/ui/FlowDiagram';
import { Activity, Users, Shield, Globe, ArrowUpRight, CheckCircle, AlertCircle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { cn } from '@/lib/utils';

const activityData = [
  { name: '00:00', logins: 120 },
  { name: '04:00', logins: 80 },
  { name: '08:00', logins: 450 },
  { name: '12:00', logins: 980 },
  { name: '16:00', logins: 850 },
  { name: '20:00', logins: 300 },
  { name: '24:00', logins: 150 },
];

const methodData = [
  { name: 'SAML 2.0', value: 65, color: '#007DC1' },
  { name: 'OIDC', value: 25, color: '#00D4FF' },
  { name: 'WS-Fed', value: 10, color: '#94A3B8' },
];

export default function Dashboard() {
  return (
    <OktaShell>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-ghost-white mb-2">SSO Dashboard</h1>
            <p className="text-slate-gray">Real-time federation health and authentication metrics.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success-green/10 border border-success-green/20">
              <div className="w-2 h-2 rounded-full bg-success-green animate-pulse" />
              <span className="text-xs font-medium text-success-green">All Systems Operational</span>
            </div>
          </div>
        </div>

        {/* Hero Section: Flow & Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <SSOCard title="Live Authentication Flow" icon={Activity} className="h-full">
              <FlowDiagram />
              <div className="mt-6 grid grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Active Sessions</p>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-bold text-ghost-white">12,450</span>
                    <span className="text-xs text-success-green flex items-center mb-1">
                      <ArrowUpRight className="w-3 h-3" /> +12%
                    </span>
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Avg. Latency</p>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-bold text-ghost-white">45ms</span>
                    <span className="text-xs text-success-green flex items-center mb-1">
                      <CheckCircle className="w-3 h-3" /> Optimal
                    </span>
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-xs text-slate-gray uppercase tracking-wider mb-1">Failed Logins</p>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-bold text-ghost-white">0.2%</span>
                    <span className="text-xs text-success-green flex items-center mb-1">
                      <Shield className="w-3 h-3" /> Low
                    </span>
                  </div>
                </div>
              </div>
            </SSOCard>
          </div>

          <div className="lg:col-span-1 space-y-6">
            <SSOCard title="Auth Methods" icon={Globe}>
              <div className="h-48 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={methodData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {methodData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center flex-col pointer-events-none">
                  <span className="text-2xl font-bold text-ghost-white">100%</span>
                  <span className="text-xs text-slate-gray">Traffic</span>
                </div>
              </div>
              <div className="space-y-3 mt-4">
                {methodData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-slate-gray">{item.name}</span>
                    </div>
                    <span className="text-sm font-bold text-ghost-white">{item.value}%</span>
                  </div>
                ))}
              </div>
            </SSOCard>
          </div>
        </div>

        {/* Activity Timeline & Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <SSOCard title="Sign-in Activity (24h)" icon={Users} className="lg:col-span-2 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="colorLogins" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00D4FF" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00D4FF" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                <XAxis dataKey="name" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181B', borderColor: '#333', borderRadius: '8px' }}
                  itemStyle={{ color: '#00D4FF' }}
                />
                <Area type="monotone" dataKey="logins" stroke="#00D4FF" fillOpacity={1} fill="url(#colorLogins)" />
              </AreaChart>
            </ResponsiveContainer>
          </SSOCard>

          <SSOCard title="Federation Health" icon={Activity}>
            <div className="space-y-4">
              {[
                { name: 'Salesforce', status: 'operational', latency: '120ms' },
                { name: 'Slack', status: 'operational', latency: '85ms' },
                { name: 'Workday', status: 'degraded', latency: '450ms' },
                { name: 'AWS SSO', status: 'operational', latency: '95ms' },
              ].map((app) => (
                <div key={app.name} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      app.status === 'operational' ? "bg-success-green" : "bg-warning-amber animate-pulse"
                    )} />
                    <span className="text-sm font-medium text-ghost-white">{app.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-gray">{app.latency}</span>
                    {app.status === 'degraded' && <AlertCircle className="w-4 h-4 text-warning-amber" />}
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 py-2 text-sm text-electric-cyan hover:text-white transition-colors border border-electric-cyan/30 rounded-lg hover:bg-electric-cyan/10">
              View All Connections
            </button>
          </SSOCard>
        </div>
      </div>
    </OktaShell>
  );
}
