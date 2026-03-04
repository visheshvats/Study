# Day 2: React Fundamentals II

## 📖 3-Minute Concept Lesson

### 1. State with `useState`

**What it is:**  
State is data that a component owns and can change over time. When state changes, React re-renders the component to reflect the new data.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  //     ↑       ↑            ↑
  //  current  updater    initial value
  
  return <button onClick={() => setCount(count + 1)}>
    Clicked {count} times
  </button>;
}
```

**When to use:**  
Use state when a component needs to "remember" something that changes based on user interaction or time.

**Common mistakes:**
- ❌ Directly mutating state: `count = count + 1` → NO!
- ❌ Forgetting to import `useState` from React
- ❌ Calling setter functions without parentheses: `onClick={setCount(5)}` → infinite loop!
- ❌ Using state for values that never change (use constants instead)

**Tiny example:**
```jsx
// ❌ Wrong - directly mutating
const [count, setCount] = useState(0);
count = count + 1; // NO! This won't trigger re-render

// ✅ Correct - using setter
const [count, setCount] = useState(0);
setCount(count + 1); // YES! React knows to re-render
```

**Props vs State:**
- **Props:** Passed from parent → child, read-only
- **State:** Owned by the component, can be changed

---

### 2. Rendering Lists with `.map()`

**What it is:**  
Use JavaScript's `.map()` to transform an array of data into an array of JSX elements.

```jsx
const fruits = ['Apple', 'Banana', 'Cherry'];

function FruitList() {
  return (
    <ul>
      {fruits.map(fruit => (
        <li>{fruit}</li>
      ))}
    </ul>
  );
}
```

**When to use:**  
Whenever you have an array of data you want to display as components or elements.

**Common mistakes:**
- ❌ Forgetting curly braces around `.map()` in JSX
- ❌ Not returning JSX from the map callback
- ❌ Mapping without keys (we'll fix this next!)

**Tiny example:**
```jsx
// ❌ Wrong - not returning anything
{items.map(item => {
  <li>{item}</li>; // Missing return!
})}

// ✅ Correct - implicit return with parentheses
{items.map(item => (
  <li>{item}</li>
))}

// ✅ Also correct - explicit return
{items.map(item => {
  return <li>{item}</li>;
})}
```

---

### 3. Keys

**What it is:**  
A special `key` prop that helps React identify which items in a list have changed, been added, or removed.

```jsx
const todos = [
  { id: 1, text: 'Learn React' },
  { id: 2, text: 'Build a project' }
];

function TodoList() {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  );
}
```

**When to use:**  
ALWAYS when rendering lists with `.map()`.

**Common mistakes:**
- ❌ Using array index as key: `key={index}` → Only if list never changes
- ❌ Using non-unique values as keys
- ❌ Forgetting keys entirely (React will warn you!)
- ❌ Using random values: `key={Math.random()}` → breaks React's optimization

**Tiny example:**
```jsx
// ❌ Bad - using index (only OK if list is static)
{items.map((item, index) => (
  <li key={index}>{item}</li>
))}

// ✅ Good - using unique ID
{items.map(item => (
  <li key={item.id}>{item.name}</li>
))}
```

**Why keys matter:**  
Without keys, React can't track items efficiently. This causes:
- ❌ Performance issues
- ❌ Bugs with component state
- ❌ Incorrect UI updates

---

## 🔑 Key Takeaways

1. **State** = Data a component owns and can change (use `useState`)
2. **Lists** = Use `.map()` to render arrays of data
3. **Keys** = REQUIRED for lists, must be unique and stable

---

## ⚠️ Interview Tips

**Common questions:**

> **"What's the difference between props and state?"**  
> **Answer:** Props are passed from parent and read-only. State is owned by the component and can be updated using a setter function.

> **"Why do we need keys when rendering lists?"**  
> **Answer:** Keys help React identify which items changed, were added, or removed. This optimizes re-rendering and prevents bugs.

> **"Can you use array index as a key?"**  
> **Answer:** Only if the list is static and never reordered. Otherwise, use unique identifiers like IDs.

---

## ✅ Self-Check Questions

Before moving to exercises:

1. Can I create state with `useState` and update it with the setter?
2. Do I know the difference between props and state?
3. Can I render a list using `.map()`?
4. Do I understand why keys are required?

If yes to all, proceed to exercises! 🎉

---

**Next:** `exercises/` folder for hands-on practice!
