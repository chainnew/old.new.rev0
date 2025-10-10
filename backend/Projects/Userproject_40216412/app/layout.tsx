import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'UserProject',
  description: 'A Next.js app for managing users',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav>
            <a href="/">Home</a>
            <a href="/users">Users</a>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  )
}