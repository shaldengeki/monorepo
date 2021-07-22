module.exports = {
  prefix: '',
  purge: {
    // enabled: process.env.NODE_ENV === 'production',
    enabled: false,
    purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html']
  },
  darkMode: 'class', // or 'media' or 'class'
  theme: {
    extend: {}
  },
  variants: {
    extend: {}
  },
  plugins: []
}
