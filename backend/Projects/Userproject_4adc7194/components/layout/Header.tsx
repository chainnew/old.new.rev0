import { Button } from '@/components/ui/button'
import { Menu, User } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-background border-b px-4 md:px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-xl font-semibold">UserProject</h1>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </header>
  )
}