import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function ThreatBadge({ level }) {
  if (level === 'CRITICAL') {
    return (
      <span className="inline-flex items-center space-x-1.5 bg-red-100 text-red-800 px-3 py-1 rounded-full text-xs font-bold border border-red-200">
        <ShieldAlert className="w-3.5 h-3.5 text-red-600" />
        <span>CRITICAL THREAT DETECTED</span>
      </span>
    );
  }

  if (level === 'WARNING') {
    return (
      <span className="inline-flex items-center space-x-1.5 bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-xs font-bold border border-amber-200">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
        <span>SUSPICIOUS HEADERS</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center space-x-1.5 bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-xs font-bold border border-emerald-200">
      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
      <span>VERIFIED SAFE</span>
    </span>
  );
}