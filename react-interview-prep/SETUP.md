# Quick Setup Guide

## For Each Day's Exercises

When you're ready to start coding exercises, you'll need a React environment. Here's how to set it up quickly:

### Option 1: Using Vite (Recommended - Fast!)

```bash
cd /home/dev/Documents/Study/react-interview-prep/day1/mini-project
npm create vite@latest . -- --template react
npm install
npm run dev
```

### Option 2: Using Create React App

```bash
cd /home/dev/Documents/Study/react-interview-prep/day1/mini-project
npx create-react-app .
npm start
```

### Option 3: Simple HTML + React (For Quick Tests)

Create a single `index.html` file:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>React Practice</title>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    // Your React code here
    function App() {
      return <h1>Hello React!</h1>;
    }

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  </script>
</body>
</html>
```

Open in browser: `file:///path/to/index.html`

---

## What I Recommend

- **For exercises 1-3:** Use Option 3 (single HTML file) for speed
- **For mini-project:** Use Option 1 (Vite) for a real development experience

---

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 5173 (Vite default)
fuser -k 5173/tcp
```

**Can't see changes?**
- Make sure dev server is running
- Check browser console for errors
- Hard refresh: `Ctrl + Shift + R`

---

## Ready to Code?

1. Pick your setup method
2. Start with Exercise 1 in `day1/exercises/`
3. Complete all 3 exercises
4. Answer the interview question
5. Build the mini-project

**Let's go!** 🚀
