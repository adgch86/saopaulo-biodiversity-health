import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy API requests to FastAPI backend
  async rewrites() {
    // In Docker, api service resolves to the container
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: '/maps/:path*',
        destination: `${apiUrl}/maps/:path*`,
      },
    ];
  },

  // Output standalone for Docker
  output: 'standalone',

  // Disable strict mode for Leaflet compatibility
  reactStrictMode: false,
};

export default withNextIntl(nextConfig);
