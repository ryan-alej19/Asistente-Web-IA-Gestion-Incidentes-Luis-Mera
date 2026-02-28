import React from 'react';

export const GeminiLogo = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 24C12 17.3726 6.62742 12 0 12C6.62742 12 12 6.62742 12 0C12 6.62742 17.3726 12 24 12C17.3726 12 12 17.3726 12 24Z" fill="url(#gemini-gradient-main)" />
        <defs>
            <linearGradient id="gemini-gradient-main" x1="0" y1="12" x2="24" y2="12" gradientUnits="userSpaceOnUse">
                <stop stopColor="#4A90E2" />
                <stop offset="0.5" stopColor="#A865C9" />
                <stop offset="1" stopColor="#FF7B7B" />
            </linearGradient>
        </defs>
    </svg>
);

export const VirusTotalLogo = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10.86 21.94c.32.06.65.06.97 0a9.05 9.05 0 0 0 7.4-6.4 8.88 8.88 0 0 0-1.2-8.32l-1.63 2.18a6.11 6.11 0 0 1 .74 5.38 6.27 6.27 0 0 1-5.12 4.43c-3 .54-5.83-1.1-6.9-3.82l-2.5 1.34A8.96 8.96 0 0 0 10.86 21.94z" fill="#394EFF" />
        <path d="M11.7.06A8.93 8.93 0 0 0 2.22 6.02l2.5 1.35a6.22 6.22 0 0 1 6.56-4.13c2.7.27 4.9 2.18 5.6 4.8l1.63-2.19A8.99 8.99 0 0 0 11.7.06z" fill="#394EFF" />
        <path d="M6.28 14.3a6.23 6.23 0 0 1-.22-6.57L3.55 6.39a8.97 8.97 0 0 0 .32 9.5l2.4-1.58z" fill="#394EFF" />
    </svg>
);

export const MetaDefenderLogo = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7V12C2 17.52 6.28 22.14 12 23.86C17.72 22.14 22 17.52 22 12V7L12 2ZM12 4.3L19.5 8.05V12C19.5 16.23 16.32 19.89 12 21.32C7.68 19.89 4.5 16.23 4.5 12V8.05L12 4.3Z" fill="#00AEEF" />
        <path d="M11.02 16.5H12.98V14.5H11.02V16.5ZM11.02 12.5H12.98V7.5H11.02V12.5Z" fill="#00AEEF" />
    </svg>
);
