import { notFound } from 'next/navigation'

// This would typically fetch from an API
const users = [
  { id: 1, name: 'John Doe', email: 'john@example.com', bio: 'Software Engineer' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', bio: 'Designer' },
]

interface PageProps {
  params: {
    id: string
  }
}

export default function UserDetailPage({ params }: PageProps) {
  const user = users.find((u) => u.id === parseInt(params.id))

  if (!user) {
    notFound()
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <p>Email: {user.email}</p>
      <p>Bio: {user.bio}</p>
      <a href="/users">Back to Users</a>
    </div>
  )
}