import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy API requests to FastAPI backend in development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/maps/:path*',
        destination: 'http://localhost:8000/maps/:path*',
      },
    ];
  },

  // Output standalone for Docker
  output: 'standalone',

  // Disable strict mode for Leaflet compatibility
  reactStrictMode: false,
};

export default withNextIntl(nextConfig);
