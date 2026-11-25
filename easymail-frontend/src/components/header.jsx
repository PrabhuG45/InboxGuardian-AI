import React from 'react';
import { Mail, Search, RefreshCw, ShieldCheck } from 'lucide-react';

export default function Header({ userEmail, searchQuery, setSearchQuery, onRefresh, isLoading }) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
      {/* Brand Logo */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-sm">
          <Mail className="w-5 h-5" />
        </div>
        <span className="text-lg font-bold text-slate-900 tracking-tight">Inbox Guardian AI</span>
      </div>

      {/* Search Input Bar */}
      <div className="flex-1 max-w-md mx-6 relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search sender, subject, or content..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-slate-100 focus:bg-white text-slate-800 text-xs pl-10 pr-4 py-2.5 rounded-xl border border-transparent focus:border-blue-500 outline-none transition-all"
        />
      </div>

      {/* User Controls & Status */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onRefresh}
          disabled={isLoading}
          title="Refresh Feed"
          className="p-2.5 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-xl transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
        </button>

        <div className="flex items-center space-x-2 bg-slate-100 px-3.5 py-2 rounded-xl text-xs text-slate-700 font-medium border border-slate-200">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>{userEmail || 'prabhu@example.com'}</span>
        </div>
      </div>
    </header>
  );
}