/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // !! PERIGO !!
    // Isso permite que o build termine mesmo que existam erros de tipo.
    ignoreBuildErrors: true,
  },
  eslint: {
    // Isso permite que o build termine mesmo que existam erros de lint.
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
