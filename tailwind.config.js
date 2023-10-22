/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./server/**/*.{html,js}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "sans-serif"],
        poppins: ["Poppins", "sans-serif"],
      },
    },
  },
  plugins: [],
};
