export default function ContactPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">Contact Us</h1>
      <p className="text-lg">For inquiries about UserProject, reach out via email: info@userproject.com</p>
      <Link href="/" className="mt-8 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
        Back to Home
      </Link>
    </main>
  );
}