import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  // Public routes
  publicRoutes: ["/", "/sign-in", "/sign-up"],
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};