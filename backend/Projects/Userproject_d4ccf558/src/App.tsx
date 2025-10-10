import { Layout } from "@/components/Layout";
import { Toaster } from "@/components/ui/toaster";

export default function App() {
  return (
    <div className="min-h-screen bg-background">
      <Layout>
        {/* Main content will go here */}
        <div className="p-6">
          <h1 className="text-3xl font-bold">UserProject Dashboard</h1>
          <p className="mt-2 text-muted-foreground">Welcome to your project wireframe.</p>
        </div>
      </Layout>
      <Toaster />
    </div>
  );
}