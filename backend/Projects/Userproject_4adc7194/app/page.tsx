import { UserButton, SignedIn, SignedOut, RedirectToSignIn } from "@clerk/nextjs";

export default function Home() {
  return (
    <main>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
        <p>Welcome to UserProject!</p>
      </SignedIn>
    </main>
  );
}