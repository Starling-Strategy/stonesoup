export default function StyleTestPage() {
  return (
    <div>
      {/* Inline style test - should always work */}
      <div style={{ backgroundColor: 'red', color: 'white', padding: '20px', margin: '20px' }}>
        <h1>Inline Style Test</h1>
        <p>If you can see this with red background and white text, CSS is loading.</p>
      </div>
      
      {/* Tailwind test */}
      <div className="bg-blue-500 text-white p-5 m-5 rounded">
        <h1 className="text-2xl font-bold">Tailwind Test</h1>
        <p>This should have blue background if Tailwind is working.</p>
      </div>
      
      {/* Custom theme test */}
      <div className="bg-card text-card-foreground p-5 m-5 rounded border">
        <h1 className="text-2xl font-bold">Theme Test</h1>
        <p>This uses custom theme colors.</p>
      </div>
      
      {/* Body background test */}
      <div className="p-5 m-5">
        <p>Body background color: <span className="font-mono bg-gray-100 px-2">hsl(var(--background))</span></p>
        <p>CSS variable --background: <span className="font-mono bg-gray-100 px-2">0 0% 100%</span></p>
      </div>
    </div>
  );
}