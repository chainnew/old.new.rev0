/** @type {import('next').NextConfig} */
const nextConfig = {
  // Clerk recommends this for production
  experimental: {
    serverComponentsExternalPackages: ['@clerk/nextjs'],
  },
};

module.exports = nextConfig;