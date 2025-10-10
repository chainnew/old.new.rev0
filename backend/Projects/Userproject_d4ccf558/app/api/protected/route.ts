import { NextRequest, NextResponse } from 'next/server';
import { verifyJWT } from '@/lib/clerk-jwt';

export async function GET(request: NextRequest) {
  const claims = await verifyJWT(request);

  if (!claims) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  return NextResponse.json({ message: 'Protected data', userId: claims.sub });
}