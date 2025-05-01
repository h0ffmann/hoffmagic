/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/hoffmagic/templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'], // Example: Clean sans-serif (adjust as needed)
        serif: ['Lora', 'ui-serif', 'Georgia', 'serif'], // Example: Elegant serif (adjust as needed)
        mono: ['JetBrains Mono', 'monospace'], // Explicitly define mono
      },
      colors: {
        // Re-map to match the target theme (adjust hex codes if needed)
        brand: {
          'primary-bg': '#1a1a1a',    // Main dark background (slightly lighter than pure black)
          'secondary-bg': '#2c2c2c',  // Slightly lighter dark for code blocks, inputs
          'text-primary': '#e0e0e0', // Primary light text
          'text-secondary': '#a0a0a0',// Secondary lighter text (e.g., dates)
          'accent': '#2ecc71',        // Bright Green accent
          'border-color': '#444444',  // Subtle borders
        },
        // Deprecate old colors if no longer needed
        // 'brand-primary': '#3d5a80',
        // 'brand-secondary': '#98c1d9',
        // 'brand-accent': '#ee6c4d',
        // 'brand-light': '#e0fbfc',
        // 'brand-dark': '#293241',
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.brand-dark'),
            a: {
              color: theme('colors.brand-accent'),
              '&:hover': {
                color: theme('colors.brand-primary'),
              },
            },
            h1: {
              fontFamily: theme('fontFamily.serif').join(', '),
              color: theme('colors.brand-dark'),
            },
            h2: {
              fontFamily: theme('fontFamily.serif').join(', '),
              color: theme('colors.brand-dark'),
            },
            h3: {
              fontFamily: theme('fontFamily.serif').join(', '),
              color: theme('colors.brand-dark'),
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
