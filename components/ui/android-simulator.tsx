"use client";

import { useState } from "react";
import { RefreshCw, Home, ArrowLeft, Menu, Smartphone } from "lucide-react";
import { cn } from "@/lib/utils";
import { sanitizeUrl } from "@/lib/sanitize-url";

export function AndroidSimulator() {
  const [url, setUrl] = useState("http://localhost:3000");
  const [showBrowserUI, setShowBrowserUI] = useState(false);
  const [showHomeScreen, setShowHomeScreen] = useState(false);

  const refreshPreview = () => {
    const iframe = document.querySelector('[data-android-frame]') as HTMLIFrameElement;
    if (iframe) iframe.src = sanitizeUrl(iframe.src);
  };

  const handleUrlChange = (newUrl: string) => {
    setUrl(newUrl);
  };

  const loadUrl = () => {
    const iframe = document.querySelector('[data-android-frame]') as HTMLIFrameElement;
    if (iframe) iframe.src = sanitizeUrl(url);
  };

  return (
    <div className="h-full flex flex-col items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black p-8 gap-4">
      {/* URL Controls */}
      <div className="flex items-center gap-2 px-4 py-2 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg">
        <input
          type="text"
          value={url}
          onChange={(e) => handleUrlChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              loadUrl();
            }
          }}
          className="w-[300px] px-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded text-white/80 placeholder-white/30 focus:outline-none focus:border-green-500/50 font-mono"
          placeholder="Enter URL..."
        />
        <button
          onClick={refreshPreview}
          className="p-1.5 rounded bg-green-600 hover:bg-green-700 text-white transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setShowBrowserUI(!showBrowserUI)}
          className={cn(
            "px-3 py-1.5 rounded text-xs font-medium transition-colors",
            showBrowserUI
              ? "bg-green-600 text-white"
              : "bg-white/10 text-white/60 hover:bg-white/20"
          )}
          title="Toggle Chrome UI"
        >
          Chrome
        </button>
        <button
          onClick={() => setShowHomeScreen(!showHomeScreen)}
          className={cn(
            "px-3 py-1.5 rounded text-xs font-medium transition-colors",
            showHomeScreen
              ? "bg-green-600 text-white"
              : "bg-white/10 text-white/60 hover:bg-white/20"
          )}
          title="Toggle Home Screen"
        >
          Home Screen
        </button>
      </div>

      {/* Pixel 9 Pro Device Frame */}
      <div className="relative" style={{ width: '412px', height: '915px' }}>
        {/* Device Bezel */}
        <div className="absolute inset-0 bg-gradient-to-b from-gray-950 to-gray-900 rounded-[50px] shadow-2xl border-[12px] border-gray-950 overflow-hidden">
          {/* Camera Punch Hole */}
          <div className="absolute top-[18px] left-1/2 -translate-x-1/2 w-[12px] h-[12px] bg-gray-950 rounded-full z-50 border-2 border-gray-800" />
          
          {/* Status Bar */}
          <div className="absolute top-0 left-0 right-0 h-[44px] bg-white z-40 flex items-center justify-between px-6">
            <div className="text-[11px] text-gray-900 font-medium">9:41</div>
            <div className="flex items-center gap-1.5">
              <svg className="w-[14px] h-[14px] text-gray-700" viewBox="0 0 24 24" fill="currentColor">
                <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z" />
              </svg>
              <svg className="w-[14px] h-[14px] text-gray-700" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 1H7c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-2-2-2zm0 18H7V5h10v14z" />
              </svg>
              <div className="text-[11px] text-gray-900 font-medium">100%</div>
            </div>
          </div>

          {/* Screen Content - Conditional View */}
          <div className="absolute top-[44px] left-0 right-0 bottom-[48px] bg-white overflow-hidden">
            {showHomeScreen ? (
              // Android Home Screen
              <div className="h-full bg-gradient-to-br from-slate-900 to-slate-800 p-6 relative">
                {/* Search Bar */}
                <div className="mb-6 px-4 py-3 bg-white/10 backdrop-blur-sm rounded-full flex items-center gap-3">
                  <svg className="w-5 h-5 text-white/70" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                  </svg>
                  <span className="text-sm text-white/70">Search</span>
                </div>

                <div className="grid grid-cols-4 gap-6">
                  {/* Apps Grid */}
                  {['Chrome', 'Gmail', 'Maps', 'Play Store', 'Photos', 'YouTube', 'Drive', 'Calendar', 'Keep', 'Clock', 'Camera', 'Messages'].map((app, i) => (
                    <div key={i} className="flex flex-col items-center gap-2">
                      <div className="w-14 h-14 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center shadow-lg">
                        <span className="text-2xl">{['🌐', '📧', '🗺️', '🛍️', '📷', '📺', '💾', '📅', '📝', '⏰', '📸', '💬'][i]}</span>
                      </div>
                      <span className="text-[9px] text-white text-center">{app}</span>
                    </div>
                  ))}
                </div>

                {/* Google Search Bar at Bottom */}
                <div className="absolute bottom-20 left-4 right-4 px-4 py-3 bg-white rounded-full flex items-center gap-3 shadow-2xl">
                  <svg className="w-6 h-6" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span className="text-sm text-gray-700 flex-1">Search</span>
                  <svg className="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
              </div>
            ) : showBrowserUI ? (
              // Chrome Browser UI
              <div className="flex flex-col h-full">
                {/* Chrome Address Bar */}
                <div className="flex items-center gap-2 px-3 py-2 bg-white border-b border-gray-200">
                  <div className="flex-1 flex items-center gap-2 px-3 py-1.5 bg-[#F1F3F4] rounded-full">
                    <svg className="w-3.5 h-3.5 text-gray-500" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                    <span className="text-[10px] text-gray-700 truncate">{url.replace('http://', '').replace('https://', '')}</span>
                  </div>
                  <svg className="w-4 h-4 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/>
                  </svg>
                </div>
                
                {/* Chrome Content */}
                <div className="flex-1 relative">
                  <iframe
                    data-android-frame
                    src={sanitizeUrl(url)}
                    className="w-full h-full bg-white border-0"
                    sandbox="allow-same-origin allow-scripts allow-forms allow-modals allow-popups"
                    title="Android Preview"
                  />
                </div>
                
                {/* Chrome Bottom Bar (Optional) */}
                <div className="flex items-center justify-around px-4 py-2 bg-white border-t border-gray-200">
                  <svg className="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                  </svg>
                  <svg className="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 14l9-5-9-5-9 5 9 5z"/><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222"/>
                  </svg>
                  <svg className="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 6h16M4 12h16M4 18h16"/>
                  </svg>
                </div>
              </div>
            ) : (
              // Direct App View
              <iframe
                data-android-frame
                src={sanitizeUrl(url)}
                className="w-full h-full bg-white border-0"
                sandbox="allow-same-origin allow-scripts allow-forms allow-modals allow-popups"
                title="Android Preview"
              />
            )}
          </div>

          {/* Navigation Bar */}
          <div className="absolute bottom-0 left-0 right-0 h-[48px] bg-white border-t border-gray-200 flex items-center justify-around px-8 z-40">
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <ArrowLeft className="w-5 h-5 text-gray-700" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Home className="w-5 h-5 text-gray-700" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Menu className="w-5 h-5 text-gray-700" />
            </button>
          </div>
        </div>

        {/* Power Button */}
        <div className="absolute right-[-3px] top-[200px] w-[3px] h-[60px] bg-gray-800 rounded-r" />
        <div className="absolute right-[-3px] top-[280px] w-[3px] h-[50px] bg-gray-800 rounded-r" />
      </div>

      {/* Device Info */}
      <div className="flex items-center gap-2 px-4 py-2 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg">
        <Smartphone className="w-4 h-4 text-green-400" />
        <div className="text-xs">
          <div className="text-white/90 font-semibold">Pixel 9 Pro</div>
          <div className="text-white/50 text-[10px]">412 × 915</div>
        </div>
      </div>
    </div>
  );
}
