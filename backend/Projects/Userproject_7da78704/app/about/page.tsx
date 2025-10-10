export default function AboutPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">About UserProject</h1>
      <p className="text-lg">This project demonstrates a basic Next.js setup using the App Router with TypeScript.</p>
      <a href="/" className="mt-8 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
        Back to Home
      </a>
    </main>
  );
}