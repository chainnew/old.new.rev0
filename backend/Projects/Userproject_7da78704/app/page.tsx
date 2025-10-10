import { UserButton, SignedIn, SignedOut, RedirectToSignIn } from '@clerk/nextjs';

export default function Home() {
  return (
    <main>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
        <h1>Welcome to UserProject</h1>
        <p>You are signed in!</p>
      </SignedIn>
    </main>
  );
}