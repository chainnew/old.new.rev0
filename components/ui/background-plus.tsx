"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getTheme, loadTheme } from "@/lib/themes";

interface BackgroundPlusProps {
  themeId?: string;
}

export function BackgroundPlus({ themeId }: BackgroundPlusProps) {
  const [mounted, setMounted] = useState(false);
  const [currentTheme, setCurrentTheme] = useState('midnight');

  useEffect(() => {
    setMounted(true);
    const savedTheme = loadTheme();
    setCurrentTheme(savedTheme);
  }, []);

  useEffect(() => {
    if (themeId) {
      setCurrentTheme(themeId);
    }
  }, [themeId]);

  if (!mounted) return null;

  const theme = getTheme(currentTheme);

  return (
    <div className={`fixed inset-0 -z-10 overflow-hidden bg-gradient-to-br ${theme.background}`}>
      {/* Animated plus pattern */}
      {Array.from({ length: 50 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute"
          initial={{
            opacity: 0,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
          }}
          animate={{
            opacity: [0.1, 0.3, 0.1],
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
          }}
          transition={{
            duration: Math.random() * 20 + 10,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          <svg width="20" height="20" viewBox="0 0 20 20">
            <path
              d="M10 0v20M0 10h20"
              stroke={theme.dotColor}
              strokeWidth="1"
            />
          </svg>
        </motion.div>
      ))}
    </div>
  );
}

interface PlusPatternBackgroundProps {
  plusColor?: string;
  backgroundColor?: string;
  plusSize?: number;
  className?: string;
  style?: React.CSSProperties;
  fade?: boolean;
  [key: string]: any;
}

export const BackgroundPlusPattern: React.FC<PlusPatternBackgroundProps> = ({
  plusColor = '#fb3a5d',
  backgroundColor = 'transparent',
  plusSize = 60,
  className,
  fade = true,
  style,
  ...props
}) => {
  const encodedPlusColor = encodeURIComponent(plusColor);

  const maskStyle: React.CSSProperties = fade
    ? {
        maskImage: 'radial-gradient(circle, white 10%, transparent 90%)',
        WebkitMaskImage: 'radial-gradient(circle, white 10%, transparent 90%)',
      }
    : {};

  //  SVG taken from https://heropatterns.com/
  const backgroundStyle: React.CSSProperties = {
    backgroundColor,
    backgroundImage: `url("data:image/svg+xml,%3Csvg width='${plusSize}' height='${plusSize}' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='${encodedPlusColor}' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
    ...maskStyle,
    ...style,
  };

  return (
    <div
      className={`absolute inset-0 h-full w-full ${className}`}
      style={backgroundStyle}
      {...props}
    />
  );
};

export default BackgroundPlus;
