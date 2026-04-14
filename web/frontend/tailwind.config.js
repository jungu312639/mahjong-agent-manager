/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ide-bg': '#1e1e1e',
        'ide-sidebar': '#252526',
        'ide-panel': '#2d2d2d',
        'ide-text': '#cccccc',
        'ide-accent': '#007acc',
      }
    },
  },
  plugins: [],
}
