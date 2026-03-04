# Exercise 1: useState Basics (10 mins)

## 🎯 Goal
Use `useState` to create an interactive counter.

## 📝 Instructions

Create a `Counter.jsx` component that:
- Has a state variable `count` starting at 0
- Displays the current count
- Has 3 buttons:
  - "Increment" (adds 1)
  - "Decrement" (subtracts 1)
  - "Reset" (sets to 0)

**Starter code:**
```jsx
import { useState } from 'react';

function Counter() {
  // TODO: Create state here
  
  return (
    <div>
      <h2>Count: {/* Display count here */}</h2>
      <button onClick={/* Add increment function */}>Increment</button>
      <button onClick={/* Add decrement function */}>Decrement</button>
      <button onClick={/* Add reset function */}>Reset</button>
    </div>
  );
}

export default Counter;
```

## ✅ Acceptance Criteria
- [ ] Counter starts at 0
- [ ] Increment button increases count by 1
- [ ] Decrement button decreases count by 1
- [ ] Reset button sets count back to 0
- [ ] Display updates when buttons are clicked

## 🐛 Edge Cases
- What happens if you click decrement when count is 0? (It should go negative, that's OK)
- Bonus: Prevent count from going below 0

## 📋 Self-Review Checklist
- [ ] Imported `useState` from 'react'
- [ ] Used array destructuring: `const [count, setCount] = useState(0)`
- [ ] Called setter functions correctly (not `setCount(5)` directly in onClick)
- [ ] Count updates visually when clicking buttons

## 💡 Hint

Remember:
- `onClick` needs a FUNCTION, not a function call
- ✅ Correct: `onClick={() => setCount(count + 1)}`
- ❌ Wrong: `onClick={setCount(count + 1)}` (calls immediately!)

---

**Time limit:** 10 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 2!
