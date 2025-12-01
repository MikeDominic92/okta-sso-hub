import React from 'react';
import { Search, Bell, User } from 'lucide-react';

export function OktaHeader() {
    return (
        <header className="h-16 border-b border-white/5 bg-obsidian-black/80 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-8 ml-64">
            <div className="flex items-center gap-4 w-96">
                <div className="relative w-full group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-gray group-focus-within:text-electric-cyan transition-colors" />
                    <input
                        type="text"
                        placeholder="Search applications, users, or policies..."
                        className="w-full bg-dark-surface border border-white/5 rounded-full py-2 pl-10 pr-4 text-sm text-ghost-white focus:outline-none focus:border-electric-cyan/30 transition-colors placeholder:text-slate-gray/50"
                    />
                </div>
            </div>

            <div className="flex items-center gap-6">
                <button className="relative p-2 rounded-full hover:bg-white/5 text-slate-gray hover:text-ghost-white transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-electric-cyan shadow-cyan-glow" />
                </button>

                <div className="h-8 w-px bg-white/5" />

                <div className="flex items-center gap-3">
                    <div className="text-right hidden md:block">
                        <p className="text-sm font-bold text-ghost-white">Admin User</p>
                        <p className="text-xs text-slate-gray">Super Administrator</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-okta-blue to-electric-cyan p-[2px]">
                        <div className="w-full h-full rounded-full bg-obsidian-black flex items-center justify-center">
                            <User className="w-5 h-5 text-ghost-white" />
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
