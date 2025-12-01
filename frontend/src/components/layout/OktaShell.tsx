import React from 'react';
import { OktaSidebar } from './OktaSidebar';
import { OktaHeader } from './OktaHeader';

export function OktaShell({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-obsidian-black text-ghost-white font-sans selection:bg-okta-blue/30 selection:text-electric-cyan">
            <OktaSidebar />
            <OktaHeader />
            <main className="ml-64 p-8 animate-in fade-in duration-500">
                {children}
            </main>
        </div>
    );
}
