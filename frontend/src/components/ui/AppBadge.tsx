import React from 'react';
import { cn } from '@/lib/utils';
import { Shield, Globe, Key } from 'lucide-react';

interface AppBadgeProps {
    status: 'active' | 'pending' | 'error';
    protocol: 'saml' | 'oidc' | 'ws-fed';
    className?: string;
}

export function AppBadge({ status, protocol, className }: AppBadgeProps) {
    const statusStyles = {
        active: 'bg-success-green/10 text-success-green border-success-green/20',
        pending: 'bg-warning-amber/10 text-warning-amber border-warning-amber/20',
        error: 'bg-error-red/10 text-error-red border-error-red/20',
    };

    const ProtocolIcon = {
        saml: Shield,
        oidc: Globe,
        'ws-fed': Key,
    }[protocol];

    return (
        <div className={cn("flex items-center gap-2", className)}>
            <span className={cn(
                "px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider border flex items-center gap-1.5",
                statusStyles[status]
            )}>
                <span className={cn("w-1.5 h-1.5 rounded-full",
                    status === 'active' ? "bg-success-green animate-pulse" :
                        status === 'pending' ? "bg-warning-amber" : "bg-error-red"
                )} />
                {status}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider border bg-white/5 border-white/10 text-slate-gray flex items-center gap-1">
                <ProtocolIcon className="w-3 h-3" />
                {protocol}
            </span>
        </div>
    );
}
