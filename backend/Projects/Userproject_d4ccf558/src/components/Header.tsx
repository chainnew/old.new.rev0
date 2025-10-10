import { Button } from "@/components/ui/button";
import { Bell, User as UserIcon } from "lucide-react";

export function Header() {
  return (
    <header className="border-b bg-background">
      <div className="flex h-16 items-center px-4 lg:px-6">
        <div className="flex-1">
          <h2 className="text-xl font-semibold">UserProject</h2>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="sm">
            <Bell className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <UserIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}