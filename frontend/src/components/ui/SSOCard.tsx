import React from 'react';
import { cn } from '@/lib/utils';

interface SSOCardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    title?: string;
    icon?: React.ElementType;
    className?: string;
    action?: React.ReactNode;
}

export function SSOCard({ children, title, icon: Icon, className, action, ...props }: SSOCardProps) {
    return (
        <div
            className={cn(
                "glass-panel rounded-xl p-6 relative overflow-hidden group transition-all duration-300 hover:border-okta-blue/30",
                className
            )}
            {...props}
        >
            {/* Cyan Corner Accent */}
            <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-electric-cyan/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="absolute top-0 right-0 w-px h-8 bg-gradient-to-b from-electric-cyan/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="absolute top-0 right-0 h-px w-8 bg-gradient-to-l from-electric-cyan/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            {(title || Icon) && (
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        {Icon && (
                            <div className="p-2 rounded-lg bg-okta-blue/10 border border-okta-blue/20 group-hover:border-electric-cyan/30 transition-colors">
                                <Icon className="w-5 h-5 text-okta-blue group-hover:text-electric-cyan transition-colors" />
                            </div>
                        )}
                        {title && (
                            <h3 className="text-lg font-bold text-ghost-white tracking-tight">{title}</h3>
                        )}
                    </div>
                    {action}
                </div>
            )}

            <div className="relative z-10">
                {children}
            </div>
        </div>
    );
}
