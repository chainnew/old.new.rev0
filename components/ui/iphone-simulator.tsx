"use client";

import { useState } from "react";
import { RefreshCw, Smartphone } from "lucide-react";
import { cn } from "@/lib/utils";

export function IPhoneSimulator() {
  const [url, setUrl] = useState("http://localhost:3000");
  const [showBrowserUI, setShowBrowserUI] = useState(false);
  const [showHomeScreen, setShowHomeScreen] = useState(false);

  const refreshPreview = () => {
    const iframe = document.querySelector('[data-iphone-frame]') as HTMLIFrameElement;
    if (iframe) iframe.src = iframe.src;
  };

  return (
    <div className="h-full flex flex-col items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black p-8 gap-4">
      {/* URL Controls */}
      <div className="flex items-center gap-2 px-4 py-2 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              const iframe = document.querySelector('[data-iphone-frame]') as HTMLIFrameElement;
              if (iframe) iframe.src = url;
            }
          }}
          className="w-[300px] px-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded text-white/80 placeholder-white/30 focus:outline-none focus:border-blue-500/50 font-mono"
          placeholder="Enter URL..."
        />
        <button
          onClick={refreshPreview}
          className="p-1.5 rounded bg-blue-500 hover:bg-blue-600 text-white transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setShowBrowserUI(!showBrowserUI)}
          className={cn(
            "px-3 py-1.5 rounded text-xs font-medium transition-colors",
            showBrowserUI
              ? "bg-blue-500 text-white"
              : "bg-white/10 text-white/60 hover:bg-white/20"
          )}
          title="Toggle Safari UI"
        >
          Safari
        </button>
        <button
          onClick={() => setShowHomeScreen(!showHomeScreen)}
          className={cn(
            "px-3 py-1.5 rounded text-xs font-medium transition-colors",
            showHomeScreen
              ? "bg-blue-500 text-white"
              : "bg-white/10 text-white/60 hover:bg-white/20"
          )}
          title="Toggle Home Screen"
        >
          Home Screen
        </button>
      </div>

      {/* iPhone 16 Pro Device Frame */}
      <div className="relative" style={{ width: '393px', height: '852px' }}>
        {/* Device Bezel */}
        <div className="absolute inset-0 bg-gradient-to-b from-gray-900 to-black rounded-[60px] shadow-2xl border-[14px] border-gray-950 overflow-hidden">
          {/* Dynamic Island */}
          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-[126px] h-[37px] bg-black rounded-full z-50 shadow-inner" />
          
          {/* Status Bar */}
          <div className="absolute top-0 left-0 right-0 h-[54px] bg-black/90 backdrop-blur-xl z-40 flex items-end justify-between px-8 pb-2">
            <div className="text-[11px] text-white font-semibold">9:41</div>
            <div className="flex items-center gap-1">
              <div className="text-[11px] text-white">5G</div>
              <div className="flex gap-[2px]">
                <div className="w-[3px] h-[10px] bg-white rounded-full" />
                <div className="w-[3px] h-[10px] bg-white rounded-full" />
                <div className="w-[3px] h-[10px] bg-white rounded-full" />
                <div className="w-[3px] h-[10px] bg-white rounded-full" />
              </div>
              <div className="w-[20px] h-[10px] border-2 border-white rounded-[3px] relative ml-1">
                <div className="absolute top-0 right-[-2px] w-[2px] h-[6px] bg-white rounded-r" />
                <div className="absolute inset-[2px] bg-white rounded-[1px]" />
              </div>
            </div>
          </div>

          {/* Screen Content - Conditional View */}
          <div className="absolute top-[54px] left-0 right-0 bottom-0 bg-white overflow-hidden">
            {showHomeScreen ? (
              // iOS Home Screen
              <div className="h-full bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400 p-6">
                <div className="grid grid-cols-4 gap-4">
                  {/* Row 1 */}
                  {['Messages', 'Calendar', 'Photos', 'Camera'].map((app, i) => (
                    <div key={i} className="flex flex-col items-center gap-1">
                      <div className="w-14 h-14 rounded-[14px] bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg flex items-center justify-center">
                        <span className="text-xl">📱</span>
                      </div>
                      <span className="text-[9px] text-white font-medium text-center">{app}</span>
                    </div>
                  ))}
                  
                  {/* Row 2 */}
                  {['Maps', 'Weather', 'Clock', 'Notes'].map((app, i) => (
                    <div key={i} className="flex flex-col items-center gap-1">
                      <div className="w-14 h-14 rounded-[14px] bg-gradient-to-br from-green-500 to-green-600 shadow-lg flex items-center justify-center">
                        <span className="text-xl">{['🗺️', '☀️', '⏰', '📝'][i]}</span>
                      </div>
                      <span className="text-[9px] text-white font-medium text-center">{app}</span>
                    </div>
                  ))}
                  
                  {/* Row 3 */}
                  {['Settings', 'Safari', 'Mail', 'Music'].map((app, i) => (
                    <div key={i} className="flex flex-col items-center gap-1">
                      <div className="w-14 h-14 rounded-[14px] bg-gradient-to-br from-gray-600 to-gray-700 shadow-lg flex items-center justify-center">
                        <span className="text-xl">{['⚙️', '🧭', '📧', '🎵'][i]}</span>
                      </div>
                      <span className="text-[9px] text-white font-medium text-center">{app}</span>
                    </div>
                  ))}
                  
                  {/* Row 4 */}
                  {['App Store', 'Wallet', 'Health', 'Files'].map((app, i) => (
                    <div key={i} className="flex flex-col items-center gap-1">
                      <div className="w-14 h-14 rounded-[14px] bg-gradient-to-br from-orange-500 to-red-600 shadow-lg flex items-center justify-center">
                        <span className="text-xl">{['🛍️', '💳', '❤️', '📁'][i]}</span>
                      </div>
                      <span className="text-[9px] text-white font-medium text-center">{app}</span>
                    </div>
                  ))}
                </div>
                
                {/* Dock */}
                <div className="absolute bottom-8 left-4 right-4 h-20 bg-white/20 backdrop-blur-2xl rounded-[28px] flex items-center justify-around px-4">
                  {['Phone', 'Messages', 'Safari', 'Music'].map((app, i) => (
                    <div key={i} className="w-14 h-14 rounded-[14px] bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg flex items-center justify-center">
                      <span className="text-2xl">{['📞', '💬', '🧭', '🎵'][i]}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : showBrowserUI ? (
              // Safari Browser UI
              <div className="flex flex-col h-full">
                {/* Safari Address Bar */}
                <div className="flex items-center gap-2 px-3 py-2 bg-[#F2F2F7] border-b border-gray-300">
                  <div className="flex-1 flex items-center gap-2 px-3 py-1.5 bg-white rounded-lg border border-gray-300">
                    <svg className="w-3.5 h-3.5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                      <path d="M12 6v6l4 2" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span className="text-[10px] text-gray-600 font-medium truncate">{url.replace('http://', '').replace('https://', '')}</span>
                  </div>
                  <button className="p-1 rounded-lg bg-white text-blue-500">
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                </div>
                
                {/* Safari Content */}
                <div className="flex-1 relative">
                  <iframe
                    data-iphone-frame
                    src={url}
                    className="w-full h-full bg-white border-0"
                    sandbox="allow-same-origin allow-scripts allow-forms allow-modals allow-popups"
                    title="iPhone Preview"
                  />
                </div>
                
                {/* Safari Bottom Bar */}
                <div className="flex items-center justify-around px-6 py-2 bg-[#F2F2F7] border-t border-gray-300">
                  <svg className="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                  </svg>
                  <svg className="w-5 h-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                  </svg>
                  <svg className="w-5 h-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
                  </svg>
                  <svg className="w-5 h-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
              </div>
            ) : (
              // Direct App View
              <iframe
                data-iphone-frame
                src={url}
                className="w-full h-full bg-white border-0"
                sandbox="allow-same-origin allow-scripts allow-forms allow-modals allow-popups"
                title="iPhone Preview"
              />
            )}
          </div>

          {/* Home Indicator */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-[140px] h-[5px] bg-white/30 rounded-full" />
        </div>

        {/* Side Buttons */}
        <div className="absolute left-[-4px] top-[120px] w-[3px] h-[45px] bg-gray-800 rounded-l" />
        <div className="absolute left-[-4px] top-[180px] w-[3px] h-[60px] bg-gray-800 rounded-l" />
        <div className="absolute left-[-4px] top-[255px] w-[3px] h-[60px] bg-gray-800 rounded-l" />
        <div className="absolute right-[-4px] top-[200px] w-[3px] h-[80px] bg-gray-800 rounded-r" />
      </div>

      {/* Device Info */}
      <div className="flex items-center gap-2 px-4 py-2 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg">
        <Smartphone className="w-4 h-4 text-blue-400" />
        <div className="text-xs">
          <div className="text-white/90 font-semibold">iPhone 16 Pro</div>
          <div className="text-white/50 text-[10px]">393 × 852</div>
        </div>
      </div>
    </div>
  );
}
