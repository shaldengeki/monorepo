module.exports = {
  prefix: '',
  purge: {
    // enabled: process.env.NODE_ENV === 'production',
    enabled: true,
    content: [
      './src/**/*.js',
      './src/**/*.tsx',
      './public/index.html'
    ]
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
