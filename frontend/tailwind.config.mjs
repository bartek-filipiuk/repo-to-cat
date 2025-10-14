/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'oxide-dark': '#0a0a0a',
        'oxide-darker': '#050505',
        'oxide-gray': '#1a1a1a',
        'oxide-gray-light': '#2a2a2a',
        'oxide-green': '#00ffa3',
        'oxide-green-dim': '#00cc82',
        'oxide-green-darker': '#009966',
        'oxide-text': '#e5e5e5',
        'oxide-text-dim': '#999999',
        'oxide-text-darker': '#666666',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      maxWidth: {
        'container': '1200px',
      }
    },
  },
  plugins: [],
}
