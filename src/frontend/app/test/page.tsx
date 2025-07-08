export default function TestPage() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-4">
        <h1 className="text-4xl font-bold">Test Page</h1>
        <p className="text-gray-600">If you can see this, the basic CSS is working.</p>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 border rounded bg-white">
            <h2 className="font-semibold">Card 1</h2>
            <p>Using regular Tailwind classes</p>
          </div>
          
          <div className="p-4 border rounded" style={{ backgroundColor: 'hsl(var(--card))' }}>
            <h2 className="font-semibold">Card 2</h2>
            <p>Using CSS variable directly</p>
          </div>
          
          <div className="p-4 border rounded bg-card">
            <h2 className="font-semibold">Card 3</h2>
            <p>Using bg-card class</p>
          </div>
        </div>
        
        <div className="p-4 bg-blue-100 rounded">
          <p>This uses standard Tailwind blue color</p>
        </div>
      </div>
    </div>
  );
}