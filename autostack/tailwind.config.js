const plugin = require("tailwindcss/plugin");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {
      fontFamily: {
        spaceMono: ["SpaceMono", "sans-serif"],
        manrope: ["Manrope", "sans-serif"],
      },
      colors: {
        ocean: {
          50: "#eaf0f6",
          100: "#d6e1ee",
          200: "#c2d2e5",
          300: "#aec4dc",
          400: "#9bb5d3",
          500: "#3a6ea5",
          600: "#315f8f",
          700: "#285079",
          800: "#204165",
          900: "#183351",
          950: "#10263d",
        },

        white: {
          50: "#ffffff",
          100: "#fefefe",
          200: "#fdfdfd",
          300: "#fcfcfc",
          400: "#fbfbfb",
          500: "#fbfbfb",
          600: "#fafafa",
          700: "#f9f9f9",
          800: "#f9f9f9",
          900: "#f8f8f8",
        },

        gray: {
          50: "#fafafa",
          100: "#f5f5f5",
          200: "#e5e5e5",
          300: "#d4d4d4",
          400: "#a3a3a3",
          500: "#353535",
          600: "#2a2a2a",
          700: "#1f1f1f",
          800: "#151515",
          900: "#0a0a0a",
        },

        firebrick: {
          50: "#fef2f2",
          100: "#fee2e2",
          200: "#fecaca",
          300: "#fca5a5",
          400: "#f87171",
          500: "#b22222",
          600: "#991b1b",
          700: "#7f1d1d",
          800: "#63171b",
          900: "#451a15",
          950: "#2c0a0e",
        },
      },
    },
  },
  plugins: [
    plugin(function ({ addBase, theme }) {
      addBase({
        body: {
          color: theme("colors.slate.700"),
        },
        h1: {
          fontSize: theme("fontSize.2xl"),
          fontFamily: theme("fontFamily.spaceMono"),
          color: theme("colors.slate.700"),
        },
        h2: {
          fontSize: theme("fontSize.2xl"),
          fontFamily: theme("fontFamily.spaceMono"),
        },
        p: {
          fontSize: theme("fontSize.l"),
          fontFamily: theme("fontFamily.manrope"),
        },
      });
    }),
    plugin(function ({ addComponents, theme, addVariant }) {
      addComponents({
        ".btn": {
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          padding: `${theme("py.1")} ${theme("py.2")}`,
          borderRadius: theme("borderRadius.md"),
          fontWeight: theme("fontWeight.semibold"),
          fontSize: theme("fontSize.sm"),
          lineHeight: theme("lineHeight.5"),
          border: "1px solid transparent",
          transition: "all 0.15s ease-in-out",
          cursor: "pointer",
          "&:disabled": {
            opacity: "0.6",
            cursor: "not-allowed",
          },
          "&:focus": {
            outline: "2px solid transparent",
            outlineOffset: "2px",
            ring: "2px",
            ringColor: theme("colors.blue.500"),
          },
        },

        ".btn-primary": {
          backgroundColor: theme("colors.ocean.600"),
          color: theme("colors.white.900"),
          "&:hover:not(:disabled)": {
            backgroundColor: theme("colors.ocean.700"),
          },
        },
      });
    }),
  ],
};
