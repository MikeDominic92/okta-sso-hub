import React from 'react';
import { cn } from '@/lib/utils';
import { Shield, Globe, Smartphone, Clock } from 'lucide-react';

interface PolicyRuleProps {
    name: string;
    conditions: {
        network: string;
        device: string;
        risk: string;
    };
    action: 'allow' | 'deny' | 'mfa';
}

export function PolicyRule({ name, conditions, action }: PolicyRuleProps) {
    return (
        <div className="p-4 rounded-lg bg-white/5 border border-white/5 hover:border-okta-blue/30 transition-colors group">
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-okta-blue" />
                    <span className="font-medium text-sm text-ghost-white">{name}</span>
                </div>
                <span className={cn(
                    "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border",
                    action === 'allow' ? "bg-success-green/10 text-success-green border-success-green/20" :
                        action === 'deny' ? "bg-error-red/10 text-error-red border-error-red/20" :
                            "bg-warning-amber/10 text-warning-amber border-warning-amber/20"
                )}>
                    {action === 'mfa' ? 'Prompt MFA' : action}
                </span>
            </div>

            <div className="grid grid-cols-3 gap-2">
                <div className="flex items-center gap-2 text-xs text-slate-gray bg-black/20 p-2 rounded">
                    <Globe className="w-3 h-3" />
                    <span>{conditions.network}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-gray bg-black/20 p-2 rounded">
                    <Smartphone className="w-3 h-3" />
                    <span>{conditions.device}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-gray bg-black/20 p-2 rounded">
                    <Shield className="w-3 h-3" />
                    <span>{conditions.risk} Risk</span>
                </div>
            </div>
        </div>
    );
}
