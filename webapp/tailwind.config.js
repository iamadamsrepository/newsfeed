const colors = require('tailwindcss/colors');

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        myblue: "#5be1e7",
        mydarkBlue: "#2a2c3d",
        myred: "#fd5754",
        mydarkRed: "#3d2a33",
      },
    },
  },
  plugins: [],
}