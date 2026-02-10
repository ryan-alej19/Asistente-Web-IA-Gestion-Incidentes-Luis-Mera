import React from 'react';

export const GeminiLogo = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M23.0805 1.5839C22.6185 8.1691 19.8665 14.242 13.9113 14.505C19.9272 14.8809 22.8447 20.3547 23.0039 26.2482C23.637 19.9077 27.2458 14.7712 32.7482 14.5806C26.5414 14.2882 23.5932 8.52841 23.0805 1.5839Z" fill="url(#gemini-gradient-1)" transform="translate(-5)" />
        <path d="M7.71261 4.75703C7.45899 8.35624 5.94998 11.6738 2.69344 11.8175C5.98317 12.0229 7.57795 15.0135 7.66497 18.2335C8.01099 14.7699 9.98312 11.963 12.9912 11.8588C9.59832 11.6991 7.9897 8.5526 7.71261 4.75703Z" fill="url(#gemini-gradient-2)" transform="translate(0 3)" />
        <defs>
            <linearGradient id="gemini-gradient-1" x1="13.9113" y1="1.5839" x2="32.7482" y2="26.2482" gradientUnits="userSpaceOnUse">
                <stop stopColor="#1AA6DE" />
                <stop offset="0.4" stopColor="#6C6CFF" />
                <stop offset="1" stopColor="#FF6C6C" />
            </linearGradient>
            <linearGradient id="gemini-gradient-2" x1="2.69344" y1="4.75703" x2="12.9912" y2="18.2335" gradientUnits="userSpaceOnUse">
                <stop stopColor="#1AA6DE" />
                <stop offset="1" stopColor="#FF6C6C" />
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
