/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',   // ← ここで src 配下を全部対象に
  ],
  theme: { extend: {} },
  plugins: [],
}