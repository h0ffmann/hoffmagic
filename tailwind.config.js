/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/hoffmagic/templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        'brand-primary': '#3d5a80',
        'brand-secondary': '#98c1d9',
        'brand-accent': '#ee6c4d',
        'brand-light': '#e0fbfc',
        'brand-dark': '#293241',
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
