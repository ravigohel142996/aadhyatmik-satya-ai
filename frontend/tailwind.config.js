/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#241910",
        paper: "#F6F0E6",
        card: "#FBF7F1",
        maroon: "#6E2A38",
        saffron: "#C4622D",
        gold: "#A68445",
        night: "#1A1422",
      },
      fontFamily: {
        dev: ['"Tiro Devanagari"', "serif"],
        display: ["Cormorant", "Palatino", "serif"],
        ui: ['"Avenir Next"', "Segoe UI", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
