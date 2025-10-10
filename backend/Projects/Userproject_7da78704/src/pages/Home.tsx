import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function Home() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to UserProject wireframe.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Users</CardTitle>
            <CardDescription>Overview of user base.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">1,234</div>
            <Button variant="outline" className="mt-4">View Details</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active Sessions</CardTitle>
            <CardDescription>Current online users.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">567</div>
            <Button variant="outline" className="mt-4">View Details</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Pending Actions</CardTitle>
            <CardDescription>Tasks requiring attention.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">89</div>
            <Button variant="outline" className="mt-4">View Details</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}