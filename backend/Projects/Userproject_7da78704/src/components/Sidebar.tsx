import { Button } from "@/components/ui/button";
import { HomeIcon, Users, Settings } from "lucide-react";
import { useState } from "react";

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <aside className={cn(
      "border-r bg-background transition-all duration-300",
      isOpen ? "w-64" : "w-0"
    )}>
      <div className="flex h-full flex-col">
        <div className="p-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(!isOpen)}
            className="w-full justify-start"
          >
            <span className={cn("mr-2", !isOpen && "hidden")}>Menu</span>
          </Button>
        </div>
        <nav className="flex-1 px-2 py-4">
          <ul className="space-y-2">
            <li>
              <Button variant="ghost" size="sm" className="w-full justify-start">
                <HomeIcon className={cn("h-4 w-4 mr-2", !isOpen && "mr-0")} />
                <span className={cn(!isOpen && "hidden")}>Home</span>
              </Button>
            </li>
            <li>
              <Button variant="ghost" size="sm" className="w-full justify-start">
                <Users className={cn("h-4 w-4 mr-2", !isOpen && "mr-0")} />
                <span className={cn(!isOpen && "hidden")}>Users</span>
              </Button>
            </li>
            <li>
              <Button variant="ghost" size="sm" className="w-full justify-start">
                <Settings className={cn("h-4 w-4 mr-2", !isOpen && "mr-0")} />
                <span className={cn(!isOpen && "hidden")}>Settings</span>
              </Button>
            </li>
          </ul>
        </nav>
      </div>
    </aside>
  );
}