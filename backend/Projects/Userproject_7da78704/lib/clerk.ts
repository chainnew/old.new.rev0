import { clerkClient } from '@clerk/nextjs/server';

export const getUserById = async (userId: string) => {
  return await clerkClient.users.getUser(userId);
};

// Example function to verify JWT token manually (if not using Clerk's built-in verification)
export const verifyJWT = async (token: string): Promise<boolean> => {
  try {
    // In production, use Clerk's JWT verification
    // This is a placeholder; use clerkClient.verifyToken(token) or similar
    const isValid = await clerkClient.verifyToken(token);
    return isValid;
  } catch (error) {
    console.error('JWT verification failed:', error);
    return false;
  }
};