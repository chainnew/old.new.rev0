export function Hero() {
  return (
    <section className="bg-blue-100 p-8 rounded-lg mb-8">
      <h1 className="text-4xl font-bold text-blue-800 mb-4">
        Welcome to UserProject
      </h1>
      <p className="text-lg text-gray-700">
        Manage your users with ease in this production-ready Next.js application.
      </p>
      <Link
        href="/dashboard"
        className="mt-4 inline-block bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
      >
        Go to Dashboard
      </Link>
    </section>
  );
}