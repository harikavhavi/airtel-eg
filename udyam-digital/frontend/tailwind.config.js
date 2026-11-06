/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        airtel: {
          red: "#E40520",
          dark: "#1A1A2E",
          gray: "#F5F5F5",
        },
      },
    },
  },
  plugins: [],
};

