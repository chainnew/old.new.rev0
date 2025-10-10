import { Home, Users, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'

export default function Sidebar() {
  return (
    <nav className="p-4 space-y-2">
      <Button variant="ghost" className="w-full justify-start">
        <Home className="h-4 w-4 mr-2" />
        Dashboard
      </Button>
      <Button variant="ghost" className="w-full justify-start">
        <Users className="h-4 w-4 mr-2" />
        Users
      </Button>
      <Button variant="ghost" className="w-full justify-start">
        <Settings className="h-4 w-4 mr-2" />
        Settings
      </Button>
    </nav>
  )
}