import { clerkClient } from "@clerk/nextjs/server";

export async function getUserMetadata(userId: string) {
  try {
    const user = await clerkClient.users.getUser(userId);
    return user.publicMetadata;
  } catch (error) {
    console.error("Error fetching user metadata:", error);
    return null;
  }
}