export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "fy-primary": "#e50914",
        "fy-dark": "#0b0b0f",
        "fy-deep": "#141414"
      },
      fontFamily: {
        display: ["Poppins", "sans-serif"]
      },
      boxShadow: {
        neon: "0 0 25px rgba(229, 9, 20, 0.6)"
      },
      backgroundImage: {
        "radial-fade":
          "radial-gradient(circle at top, rgba(229, 9, 20, 0.45), transparent 55%)"
      },
      keyframes: {
        "intro-flicker": {
          "0%, 100%": { opacity: 0.4 },
          "50%": { opacity: 1 }
        },
        "card-hover": {
          "0%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
          "100%": { transform: "translateY(0px)" }
        }
      },
      animation: {
        "intro-flicker": "intro-flicker 1.2s ease-in-out infinite",
        "card-hover": "card-hover 6s ease-in-out infinite"
      }
    }
  },
  plugins: []
};
