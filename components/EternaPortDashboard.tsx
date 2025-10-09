import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface PortTask {
  file_path: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  code?: string;
}

export function EternaPortDashboard() {
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [portingTasks, setPortingTasks] = useState<PortTask[]>([]);

  const componentsToPort = [
    { path: 'src/cpu/vcpu.rs', name: 'VCPU State', priority: 'high' },
    { path: 'src/cpu/exceptions.rs', name: 'Exception Handlers', priority: 'high' },
    { path: 'src/memory/stage2.rs', name: 'Stage-2 MMU', priority: 'high' },
    { path: 'src/devices/gic/mod.rs', name: 'GICv3', priority: 'medium' },
    { path: 'src/devices/timer/generic_timer.rs', name: 'Timers', priority: 'medium' },
    { path: 'src/boot.S', name: 'Boot Assembly', priority: 'high' },
  ];

  const startPort = async (filePath: string) => {
    try {
      const response = await fetch('http://localhost:8000/eterna/port', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          description: `Port ${filePath} from ARM64 to x86_64`,
          conversation_id: 'eterna-x86-port',
          target_ui: 'both'
        })
      });

      const data = await response.json();
      
      // Update tasks
      setPortingTasks(prev => [...prev, {
        file_path: filePath,
        status: 'completed',
        progress: 100,
        code: data.output?.code || ''
      }]);

      // TODO: Send data to Code Window and Planner
      console.log('Port completed:', data);
      
    } catch (error) {
      console.error('Port failed:', error);
    }
  };

  const startBulkPort = async () => {
    const paths = componentsToPort.map(c => c.path);
    
    try {
      const response = await fetch('http://localhost:8000/eterna/port/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          components: paths,
          conversation_id: 'eterna-x86-bulk'
        })
      });

      const data = await response.json();
      console.log('Bulk port:', data);
      
    } catch (error) {
      console.error('Bulk port failed:', error);
    }
  };

  return (
    <div className="w-full h-full p-4 bg-gray-900 text-white">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">ETERNA ARM→x86 Port</h1>
        <p className="text-gray-400">80k lines | Type-1 Hypervisor | Rust</p>
      </div>

      <Tabs defaultValue="components" className="w-full">
        <TabsList>
          <TabsTrigger value="components">Components</TabsTrigger>
          <TabsTrigger value="progress">Progress</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="components" className="space-y-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Core Components</h2>
            <Button onClick={startBulkPort} variant="default">
              Port All (Parallel)
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {componentsToPort.map(comp => (
              <Card key={comp.path} className="p-4 bg-gray-800 border-gray-700">
                <div className="flex flex-col space-y-3">
                  <div>
                    <h3 className="font-semibold text-lg">{comp.name}</h3>
                    <p className="text-sm text-gray-400">{comp.path}</p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      comp.priority === 'high' ? 'bg-red-900 text-red-200' :
                      comp.priority === 'medium' ? 'bg-yellow-900 text-yellow-200' :
                      'bg-green-900 text-green-200'
                    }`}>
                      {comp.priority}
                    </span>
                  </div>

                  <Button 
                    onClick={() => startPort(comp.path)}
                    size="sm"
                    variant="outline"
                  >
                    Port to x86
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="progress">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Porting Progress</h2>
            
            {portingTasks.length === 0 ? (
              <p className="text-gray-400">No ports started yet</p>
            ) : (
              portingTasks.map(task => (
                <Card key={task.file_path} className="p-4 bg-gray-800 border-gray-700">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-sm">{task.file_path}</span>
                    <span className={`px-2 py-1 text-xs rounded ${
                      task.status === 'completed' ? 'bg-green-900 text-green-200' :
                      task.status === 'in_progress' ? 'bg-blue-900 text-blue-200' :
                      task.status === 'failed' ? 'bg-red-900 text-red-200' :
                      'bg-gray-700'
                    }`}>
                      {task.status}
                    </span>
                  </div>
                  <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{width: `${task.progress}%`}}
                    />
                  </div>
                  
                  {/* Code Preview with Line Numbers */}
                  {task.code && (
                    <div className="mt-4 rounded-lg overflow-hidden border border-gray-700">
                      <div className="bg-gray-900 px-3 py-2 border-b border-gray-700">
                        <span className="text-xs text-gray-400 font-mono">Generated x86_64 Code</span>
                      </div>
                      <div className="max-h-96 overflow-auto">
                        <SyntaxHighlighter
                          language="rust"
                          style={oneDark}
                          customStyle={{
                            margin: 0,
                            padding: '1rem',
                            background: '#000000',
                            fontSize: '0.875rem',
                            lineHeight: '1.6',
                          }}
                          showLineNumbers={true}
                          lineNumberStyle={{
                            minWidth: '3em',
                            paddingRight: '1em',
                            color: 'rgba(255, 255, 255, 0.3)',
                            fontSize: '6px',
                            userSelect: 'none',
                          }}
                          wrapLines={true}
                        >
                          {task.code}
                        </SyntaxHighlighter>
                      </div>
                    </div>
                  )}
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="analysis">
          <div>
            <h2 className="text-xl font-semibold mb-4">Architecture Analysis</h2>
            <Card className="p-6 bg-gray-800 border-gray-700">
              <h3 className="font-semibold mb-4">ARM64 → x86_64 Mappings</h3>
              <div className="space-y-2 font-mono text-sm">
                <div className="flex justify-between border-b border-gray-700 py-2">
                  <span className="text-blue-400">EL2 (Exception Level 2)</span>
                  <span className="text-green-400">VMX root mode</span>
                </div>
                <div className="flex justify-between border-b border-gray-700 py-2">
                  <span className="text-blue-400">Stage-2 Translation</span>
                  <span className="text-green-400">EPT (Extended Page Tables)</span>
                </div>
                <div className="flex justify-between border-b border-gray-700 py-2">
                  <span className="text-blue-400">GICv3</span>
                  <span className="text-green-400">APIC + IO-APIC</span>
                </div>
                <div className="flex justify-between border-b border-gray-700 py-2">
                  <span className="text-blue-400">HCR_EL2</span>
                  <span className="text-green-400">VMCS controls</span>
                </div>
                <div className="flex justify-between border-b border-gray-700 py-2">
                  <span className="text-blue-400">Generic Timers</span>
                  <span className="text-green-400">TSC + APIC timer</span>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
