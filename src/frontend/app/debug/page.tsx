'use client';

import { useEffect, useState } from 'react';

export default function DebugPage() {
  const [mounted, setMounted] = useState(false);
  const [cssLoaded, setCssLoaded] = useState(false);
  
  useEffect(() => {
    setMounted(true);
    
    // Check if CSS is loaded
    const checkCSS = () => {
      const styles = window.getComputedStyle(document.body);
      const bgColor = styles.backgroundColor;
      setCssLoaded(bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent');
    };
    
    checkCSS();
    
    // Also check after a delay
    setTimeout(checkCSS, 1000);
  }, []);
  
  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Debug Information</h1>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Mounted:</strong> {mounted ? 'Yes' : 'No'}
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>CSS Loaded:</strong> {cssLoaded ? 'Yes' : 'No'}
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Body Background:</strong> {
          mounted ? window.getComputedStyle(document.body).backgroundColor : 'Not mounted'
        }
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>CSS Variable --background:</strong> {
          mounted ? window.getComputedStyle(document.documentElement).getPropertyValue('--background') : 'Not mounted'
        }
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <strong>Document Ready State:</strong> {
          mounted ? document.readyState : 'Not mounted'
        }
      </div>
      
      <h2 style={{ fontSize: '18px', marginBottom: '10px' }}>Tailwind Classes Test:</h2>
      
      <div className="bg-blue-500 text-white p-4 rounded mb-4">
        This should have blue background (Tailwind)
      </div>
      
      <div className="bg-card p-4 rounded border">
        This should use custom theme colors
      </div>
    </div>
  );
}