/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#09090b',
        foreground: '#fafafa',
        primary: '#3b82f6',
        secondary: '#27272a',
        border: '#3f3f46'
      }
    },
  },
  plugins: [],
}
