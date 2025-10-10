import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export async function GET() {
  const { userId, sessionId, getToken } = auth();

  if (!userId || !sessionId) {
    return new NextResponse("Unauthorized", { status: 401 });
  }

  // Fetch the JWT token
  const token = await getToken({ template: "userproject-jwt" });

  if (!token) {
    return new NextResponse("No token", { status: 401 });
  }

  // In production, verify the JWT manually if needed (Clerk handles it via getToken)
  // For example, using jose or jsonwebtoken library for custom verification

  return NextResponse.json({ message: "Protected data", userId, token });
}