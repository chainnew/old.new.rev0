import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  // Public routes are routes that don't require your users to be signed in to access, such as your marketing pages, or your sign in/up pages.
  publicRoutes: ["/", "/sign-in", "/sign-up"],
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};