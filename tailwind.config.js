/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./server/**/*.{html,js}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "sans-serif"],
        poppins: ["Poppins", "sans-serif"],
      },
      colors: {
        primary: "#FF91BB",
        softWhite: "#F0F0F5",
        softBlack: "#101015",
      },
    },
  },
  plugins: [],
};
