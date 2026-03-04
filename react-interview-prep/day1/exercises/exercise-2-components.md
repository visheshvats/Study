# Exercise 2: Create Components (10 mins)

## 🎯 Goal
Write two separate components and use them together.

## 📝 Instructions

Create two files:

**1. `Header.jsx`**
```jsx
// Create a Header component that displays:
// - An <h1> with text "My Portfolio"
// - A <p> with text "Welcome to my website"
```

**2. `Footer.jsx`**
```jsx
// Create a Footer component that displays:
// - A <footer> tag
// - A <p> inside with text "© 2026 My Portfolio"
```

**3. Update `App.jsx`** to use both components:
```jsx
import Header from './Header';
import Footer from './Footer';

function App() {
  // Use Header and Footer here
  // Add a <main> section in between with any content
}

export default App;
```

## ✅ Acceptance Criteria
- [ ] Three separate files: `Header.jsx`, `Footer.jsx`, `App.jsx`
- [ ] Component names start with capital letters
- [ ] Each component returns valid JSX
- [ ] App.jsx imports and uses both components

## 🐛 Edge Cases
- What if you forget to `export default` from Header or Footer?

## 📋 Self-Review Checklist
- [ ] All components are properly named (capitalized)
- [ ] All imports/exports are correct
- [ ] Code runs without import errors
- [ ] UI displays Header, main content, and Footer in order

---

**Time limit:** 10 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 3!
