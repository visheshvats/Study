# Exercise 3: Props (15 mins)

## 🎯 Goal
Pass data from parent to child using props.

## 📝 Instructions

Create a `Button.jsx` component that:
- Accepts a `text` prop (the button label)
- Accepts a `color` prop (for styling)
- Returns a `<button>` element

Then use it in `App.jsx` THREE times with different props:
1. Red button with text "Delete"
2. Green button with text "Confirm"
3. Blue button with text "Info"

**Starter code for `Button.jsx`:**
```jsx
function Button(props) {
  return (
    <button style={{ backgroundColor: props.color }}>
      {/* Display the text prop here */}
    </button>
  );
}

export default Button;
```

**In `App.jsx`:**
```jsx
import Button from './Button';

function App() {
  return (
    <div>
      {/* Use Button component 3 times with different props */}
    </div>
  );
}

export default App;
```

## ✅ Acceptance Criteria
- [ ] Button component accepts `text` and `color` props
- [ ] Button displays the text inside the `<button>`
- [ ] Button applies the background color from props
- [ ] App.jsx renders 3 buttons with different props

## 🐛 Edge Cases
- What if someone forgets to pass the `text` prop? (Undefined will show)
- Can you set a default color if `color` prop is missing?

## 📋 Self-Review Checklist
- [ ] Props are accessed correctly (`props.text`, `props.color`)
- [ ] JSX curly braces are used for dynamic values
- [ ] All three buttons display correctly with different colors
- [ ] No errors in the console

## 💡 Bonus Challenge
Refactor `Button` to use **destructuring**:
```jsx
function Button({ text, color }) {
  // Now you can use `text` and `color` directly!
}
```

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to the Interview Question!
