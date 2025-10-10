import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default function Dashboard() {
  const { userId } = auth();

  if (!userId) {
    redirect('/sign-in');
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, user {userId}!</p>
    </div>
  );
}