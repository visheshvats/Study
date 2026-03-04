# Day 5: Hooks Deep Dive II

## 📖 3-Minute Concept Lesson

### 1. useRef

**What it is:**  
`useRef` creates a mutable reference that persists across renders WITHOUT causing re-renders when changed. It has two main uses: accessing DOM elements and storing mutable values.

```jsx
import { useRef } from 'react';

function InputFocus() {
  const inputRef = useRef(null);
  
  const focusInput = () => {
    inputRef.current.focus(); // Access DOM directly!
  };
  
  return (
    <>
      <input ref={inputRef} />
      <button onClick={focusInput}>Focus Input</button>
    </>
  );
}
```

**When to use:**
- **DOM access:** Focus inputs, scroll to elements, measure elements
- **Stable values:** Store values that shouldn't trigger re-renders (timers, previous values)
- **Avoiding re-renders:** Store data that changes but doesn't affect UI

**Common mistakes:**
- ❌ Using it for data that should trigger renders (use useState instead!)
- ❌ Reading/writing during render (only in effects or handlers!)
- ❌ Forgetting `.current` to access the value
- ❌ Comparing refs in useEffect dependencies (refs don't change, so no re-run)

**Two main patterns:**

**Pattern 1: DOM Access**
```jsx
const inputRef = useRef(null);
<input ref={inputRef} />
// Later: inputRef.current.focus()
```

**Pattern 2: Stable Mutable Value**
```jsx
const countRef = useRef(0);
countRef.current += 1; // Doesn't trigger re-render!
```

**useState vs useRef:**
```jsx
// useState: Changes trigger re-renders
const [count, setCount] = useState(0);
setCount(1); // → Re-renders component

// useRef: Changes DON'T trigger re-renders  
const countRef = useRef(0);
countRef.current = 1; // → No re-render!
```

---

### 2. useMemo

**What it is:**  
`useMemo` memoizes (caches) the result of an expensive calculation, only recalculating when dependencies change.

```jsx
import { useMemo } from 'react';

function ExpensiveComponent({ items }) {
  const total = useMemo(() => {
    // This only runs when 'items' changes
    console.log('Calculating total...');
    return items.reduce((sum, item) => sum + item.price, 0);
  }, [items]);
  
  return <div>Total: ${total}</div>;
}
```

**When to use:**
- Expensive calculations (filtering, sorting large arrays)
- Preventing object recreation (for dependency arrays)
- **ONLY** when you have a proven performance problem

**When NOT to use:**
- ❌ Simple calculations (a + b)
- ❌ "Just in case" optimization
- ❌ Every single calculation
- ❌ Before measuring if there's actually a problem

**Common mistakes:**
- ❌ Premature optimization (biggest mistake!)
- ❌ Missing dependencies
- ❌ Using it everywhere (adds overhead!)
- ❌ Memoizing something that's already cheap

**Pattern:**
```jsx
const expensiveValue = useMemo(() => {
  // Expensive calculation here
  return someExpensiveCalculation(data);
}, [data]); // Only recalculate when 'data' changes
```

**Rule of thumb:** DON'T use useMemo unless:
1. You've measured and found a performance issue
2. The calculation is genuinely expensive (> 1ms)
3. It runs frequently with the same inputs

---

### 3. useCallback

**What it is:**  
`useCallback` memoizes a function, returning the same function reference across renders (unless dependencies change).

```jsx
import { useCallback } from 'react';

function Parent() {
  const [count, setCount] = useState(0);
  
  // Without useCallback: New function every render
  const handleClick = () => setCount(count + 1);
  
  // With useCallback: Same function unless dependencies change
  const handleClickMemo = useCallback(() => {
    setCount(count + 1);
  }, [count]);
  
  return <Child onClick={handleClickMemo} />;
}
```

**When to use:**
- Passing callbacks to memoized child components (with React.memo)
- Preventing useEffect from re-running unnecessarily
- Stable function references for dependencies

**When NOT to use:**
- ❌ "Just to be safe"
- ❌ Every callback function
- ❌ Without React.memo on children
- ❌ Before measuring performance

**Common mistakes:**
- ❌ Using it everywhere (premature optimization!)
- ❌ Missing dependencies (stale closures)
- ❌ Using without React.memo (no benefit!)
- ❌ Thinking it makes the function faster (it doesn't!)

**Pattern:**
```jsx
const memoizedCallback = useCallback(() => {
  // Function body
  doSomething(a, b);
}, [a, b]); // Only create new function when a or b changes
```

**Important:** `useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`

---

## 🔑 Key Takeaways

1. **useRef** = Mutable value that doesn't trigger re-renders (DOM, stable values)
2. **useMemo** = Memoize expensive calculations (use sparingly!)
3. **useCallback** = Memoize functions (for React.memo children, usually)

---

## ⚠️ Interview Tips

**Common questions:**

> **"What's the difference between useRef and useState?"**  
> **Answer:** useState causes re-renders when updated, useRef doesn't. useState is for data that affects the UI. useRef is for values you need to persist but don't want to trigger renders (DOM refs, timers, previous values).

> **"When should you use useMemo?"**  
> **Answer:** Only for expensive calculations where you've measured a performance problem. Don't use it for simple operations or "just in case." The overhead of memoization can be worse than just recalculating. Measure first, optimize second.

> **"What's the difference between useMemo and useCallback?"**  
> **Answer:** useMemo returns a memoized VALUE, useCallback returns a memoized FUNCTION. useCallback(fn, deps) is shorthand for useMemo(() => fn, deps).

> **"When should you NOT use useCallback?"**  
> **Answer:** Don't use it unless the child component is wrapped in React.memo or you need a stable reference for useEffect dependencies. Using it everywhere is premature optimization and actually adds overhead.

---

## ✅ Self-Check Questions

Before moving to exercises:

1. When would I use useRef instead of useState?
2. Can I name one expensive operation worth memoizing?
3. Why is premature optimization with useMemo bad?
4. When does useCallback actually help performance?

If yes to all, proceed to exercises! 🎉

---

**Next:** `exercises/` folder for hands-on practice!
