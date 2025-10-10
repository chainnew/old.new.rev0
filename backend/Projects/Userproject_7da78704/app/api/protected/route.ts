import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function GET() {
  const { userId, sessionId, getToken } = auth();

  if (!userId || !sessionId) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  // Optional: Verify JWT token explicitly if needed beyond Clerk's auth
  const token = await getToken({ template: 'your-jwt-template' }); // Replace with actual template if using custom JWT templates
  if (!token) {
    return new NextResponse('Invalid token', { status: 401 });
  }

  // Your protected API logic here
  return NextResponse.json({ message: 'Protected endpoint accessed', userId });
}