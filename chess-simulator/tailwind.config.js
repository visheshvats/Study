/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'chess-board': '#D0C4B4', // Light square color (example)
                'chess-dark': '#8B5A2B',  // Dark square color (example)
            }
        },
    },
    plugins: [],
}
