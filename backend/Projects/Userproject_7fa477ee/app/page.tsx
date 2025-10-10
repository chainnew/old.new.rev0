import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6">Welcome to UserProject</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
          Build a simple todo app with Next.js
        </p>
        <Button size="lg">Get Started Free</Button>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {["Fast", "Easy", "Secure"].map((f, i) => (
            <Card key={i}>
              <CardHeader><CardTitle>{f}</CardTitle></CardHeader>
              <CardContent><CardDescription>Feature description here</CardDescription></CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
