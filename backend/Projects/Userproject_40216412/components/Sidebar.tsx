import { Button } from '@/components/ui/button'
import { Home, Users, Settings, BarChart3, FileText } from 'lucide-react'

const navItems = [
  { icon: Home, label: 'Dashboard', href: '/' },
  { icon: Users, label: 'Users', href: '/users' },
  { icon: BarChart3, label: 'Analytics', href: '/analytics' },
  { icon: FileText, label: 'Reports', href: '/reports' },
  { icon: Settings, label: 'Settings', href: '/settings' },
]

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-background p-4 md:w-72">
      <nav className="space-y-2">
        {navItems.map((item) => (
          <Button
            key={item.label}
            variant="ghost"
            className="w-full justify-start"
            asChild
          >
            <a href={item.href}>
              <item.icon className="mr-3 h-4 w-4" />
              {item.label}
            </a>
          </Button>
        ))}
      </nav>
    </aside>
  )
}