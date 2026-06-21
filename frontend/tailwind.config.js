/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#fdf2f2",
          100: "#fce8e8",
          200: "#f7c5c5",
          300: "#f0a2a2",
          400: "#e35c5c",
          500: "#d61a1a",
          600: "#b80000",
          700: "#9a0000",
          800: "#7c0000",
          900: "#5e0000",
          DEFAULT: "#780000",
        },
      },
    },
  },
  plugins: [],
};