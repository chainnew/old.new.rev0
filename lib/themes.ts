export interface Theme {
  id: string;
  name: string;
  background: string;
  backgroundGradient: { from: string; via: string; to: string };
  dotColor: string;
  accentColor: string;
  textColor: string;
  borderColor: string;
  panelBg: string;
  description: string;
}

export const themes: Theme[] = [
  {
    id: 'midnight',
    name: 'Midnight',
    background: 'from-black via-gray-900 to-black',
    backgroundGradient: { from: '#000000', via: '#111827', to: '#000000' },
    dotColor: 'rgb(139, 92, 246, 0.3)',
    accentColor: 'rgb(139, 92, 246)',
    textColor: 'white',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    panelBg: 'rgba(0, 0, 0, 0.6)',
    description: 'Classic dark theme'
  },
  {
    id: 'electric',
    name: 'Electric',
    background: 'from-purple-900 via-violet-900 to-purple-900',
    backgroundGradient: { from: '#581c87', via: '#4c1d95', to: '#581c87' },
    dotColor: 'rgb(168, 85, 247, 0.4)',
    accentColor: 'rgb(168, 85, 247)',
    textColor: 'white',
    borderColor: 'rgba(168, 85, 247, 0.2)',
    panelBg: 'rgba(88, 28, 135, 0.6)',
    description: 'Electric purple vibes'
  },
  {
    id: 'ocean',
    name: 'Ocean',
    background: 'from-blue-950 via-cyan-950 to-blue-950',
    backgroundGradient: { from: '#082f49', via: '#083344', to: '#082f49' },
    dotColor: 'rgb(34, 211, 238, 0.3)',
    accentColor: 'rgb(34, 211, 238)',
    textColor: 'white',
    borderColor: 'rgba(34, 211, 238, 0.2)',
    panelBg: 'rgba(8, 47, 73, 0.6)',
    description: 'Deep ocean blue'
  },
  {
    id: 'forest',
    name: 'Forest',
    background: 'from-emerald-950 via-green-950 to-emerald-950',
    backgroundGradient: { from: '#064e3b', via: '#052e16', to: '#064e3b' },
    dotColor: 'rgb(16, 185, 129, 0.3)',
    accentColor: 'rgb(16, 185, 129)',
    textColor: 'white',
    borderColor: 'rgba(16, 185, 129, 0.2)',
    panelBg: 'rgba(6, 78, 59, 0.6)',
    description: 'Forest green tranquility'
  },
  {
    id: 'sunset',
    name: 'Sunset',
    background: 'from-orange-950 via-red-950 to-orange-950',
    backgroundGradient: { from: '#7c2d12', via: '#450a0a', to: '#7c2d12' },
    dotColor: 'rgb(251, 146, 60, 0.3)',
    accentColor: 'rgb(251, 146, 60)',
    textColor: 'white',
    borderColor: 'rgba(251, 146, 60, 0.2)',
    panelBg: 'rgba(124, 45, 18, 0.6)',
    description: 'Warm sunset orange'
  },
  {
    id: 'cream',
    name: 'Cream',
    background: 'from-amber-50 via-yellow-50 to-amber-50',
    backgroundGradient: { from: '#fffbeb', via: '#fefce8', to: '#fffbeb' },
    dotColor: 'rgb(217, 119, 6, 0.15)',
    accentColor: 'rgb(217, 119, 6)',
    textColor: 'rgb(120, 53, 15)',
    borderColor: 'rgba(217, 119, 6, 0.15)',
    panelBg: 'rgba(254, 252, 232, 0.8)',
    description: 'Soft cream light theme'
  },
  {
    id: 'slate',
    name: 'Slate',
    background: 'from-slate-200 via-gray-200 to-slate-200',
    backgroundGradient: { from: '#e2e8f0', via: '#e5e7eb', to: '#e2e8f0' },
    dotColor: 'rgb(100, 116, 139, 0.2)',
    accentColor: 'rgb(100, 116, 139)',
    textColor: 'rgb(30, 41, 59)',
    borderColor: 'rgba(100, 116, 139, 0.2)',
    panelBg: 'rgba(241, 245, 249, 0.8)',
    description: 'Professional slate gray'
  },
  {
    id: 'rose',
    name: 'Rose',
    background: 'from-rose-950 via-pink-950 to-rose-950',
    backgroundGradient: { from: '#881337', via: '#500724', to: '#881337' },
    dotColor: 'rgb(251, 113, 133, 0.3)',
    accentColor: 'rgb(251, 113, 133)',
    textColor: 'white',
    borderColor: 'rgba(251, 113, 133, 0.2)',
    panelBg: 'rgba(136, 19, 55, 0.6)',
    description: 'Elegant rose pink'
  },
  {
    id: 'cyber',
    name: 'Cyber',
    background: 'from-cyan-950 via-blue-950 to-purple-950',
    backgroundGradient: { from: '#083344', via: '#172554', to: '#581c87' },
    dotColor: 'rgb(34, 211, 238, 0.3)',
    accentColor: 'rgb(34, 211, 238)',
    textColor: 'white',
    borderColor: 'rgba(34, 211, 238, 0.2)',
    panelBg: 'rgba(8, 47, 73, 0.6)',
    description: 'Cyberpunk neon'
  },
  {
    id: 'matrix',
    name: 'Matrix',
    background: 'from-black via-green-950 to-black',
    backgroundGradient: { from: '#000000', via: '#052e16', to: '#000000' },
    dotColor: 'rgb(34, 197, 94, 0.3)',
    accentColor: 'rgb(34, 197, 94)',
    textColor: 'rgb(134, 239, 172)',
    borderColor: 'rgba(34, 197, 94, 0.2)',
    panelBg: 'rgba(0, 0, 0, 0.8)',
    description: 'The Matrix green'
  }
];

export function getTheme(id: string): Theme {
  return themes.find(t => t.id === id) || themes[0];
}

export function saveTheme(id: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('app-theme', id);
  }
}

export function loadTheme(): string {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('app-theme') || 'midnight';
  }
  return 'midnight';
}
