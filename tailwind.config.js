/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html"],
  theme: {
    screens: {
      sm: '550px',
      md: '800px',
      lg: '1200px',
      xl: '1440px',
    },
    fontFamily: {
      Sans: ['Lato', 'sans-serif'],
    },
    extend: {
      colors: {
        priColor: 'blue-800',
        secColor: '#1C0360',
      }
    },
  },
  plugins: [],
}