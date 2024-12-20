/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${
          process.env.BACKEND_URL || "http://127.0.0.1:5000"
        }/:path*`, // Replace with your backend's URL
      },
    ];
  },
};

module.exports = nextConfig;
