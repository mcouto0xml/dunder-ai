/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
         'office': ['"Courier New"', 'Courier', 'monospace'],
        'sans': ['Arial', 'Helvetica', 'sans-serif'] 
      },
      colors: {
        dm: {
          black: '#1a1a1a', 
          gray: '#f0f0f0',  
          darkgray: '#555555'
        }
      }
    },
  },
  plugins: [],
}