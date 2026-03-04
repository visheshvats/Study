# Day 4 Recap & Tomorrow's Prep

## 🎯 Day 4 Summary

Today you mastered one of the most important React hooks: useEffect!

### 1. useEffect Basics
- ✅ Performs side effects in functional components
- ✅ Runs after render (not during)
- ✅ Three syntax patterns: no deps, empty deps `[]`, specific deps `[value]`
- ✅ Used for: data fetching, subscriptions, timers, DOM manipulation

### 2. Dependency Arrays
- ✅ No array = runs after every render
- ✅ Empty `[]` = runs once on mount
- ✅ With values `[a, b]` = runs when a or b changes
- ✅ React re-runs effect when dependencies change (Object.is comparison)

### 3. Cleanup Functions
- ✅ Return function from useEffect
- ✅ Runs before next effect and on unmount
- ✅ Critical for: timers, subscriptions, event listeners, fetch requests
- ✅ Prevents memory leaks and bugs

---

## 📊 What You Built Today

- ✅ useEffect demo with different dependency arrays
- ✅ Timer with cleanup (stopwatch + countdown)
- ✅ User fetcher with loading/error states
- ✅ **GitHub User Search** with debouncing and race condition handling

---

## ⚠️ Common Mistakes You Avoided

1. ❌ Missing dependencies → ✅ Include all used props/state in array
2. ❌ No cleanup for timers → ✅ Always clear intervals/timeouts
3. ❌ No fetch abort → ✅ Use AbortController to cancel requests
4. ❌ Infinite loops → ✅ Proper dependency arrays
5. ❌ Race conditions → ✅ Cleanup cancels old requests

---

## 🧠 Key Interview Concepts Covered

### Question: "What is useEffect and when do you use it?"
**Model answer:**
- useEffect performs side effects in function components
- Side effects: anything that reaches outside the component (API calls, subscriptions, timers)
- Runs after render, not during (doesn't block UI)
- Dependency array controls when it re-runs
- Cleanup function prevents memory leaks

### Question: "Explain dependency arrays in useEffect"
**Model answer:**
- Second argument to useEffect, controls when effect runs
- **No array:** Runs after every render (rarely needed)
- **Empty `[]`:** Runs once on mount (initial data fetch)
- **With values `[a, b]`:** Runs when a or b changes
- React compares using Object.is (reference equality for objects/arrays)
- ESLint will warn if you forget dependencies

### Question: "Why do we need cleanup functions?"
**Model answer:**
- Prevent memory leaks and bugs
- Without cleanup:
  - Timers keep running after unmount
  - Event listeners accumulate
  - Subscriptions stay active
  - Fetch can update unmounted components
- Cleanup runs:
  - Before effect runs again (when deps change)
  - When component unmounts
- Examples: clearInterval, removeEventListener, abort fetch

### Question: "What's a race condition in React and how do you prevent it?"
**Model answer:**
- Multiple async operations where results arrive out of order
- Example: Search for "A", then "B" quickly. "A" results arrive after "B", showing wrong data
- **Prevention:**
  - Use AbortController to cancel previous requests
  - Return cleanup function that calls abort()
  - Check if component is still mounted before setState
- Pattern:
  ```jsx
  useEffect(() => {
    const controller = new AbortController();
    fetch(url, { signal: controller.signal })
      .then(...)
      .catch(err => {
        if (err.name === 'AbortError') return; // Ignore
        setError(err.message);
      });
    return () => controller.abort(); // Cleanup!
  }, [url]);
  ```

---

## 📝 What to Revise Tomorrow Morning (5 mins)

Before starting Day 5, quickly review:

1. **useEffect patterns:**
   ```jsx
   useEffect(() => {}, []);           // Once on mount
   useEffect(() => {}, [value]);      // When value changes
   useEffect(() => { return cleanup; }, []); // With cleanup
   ```

2. **Data fetching template:**
   ```jsx
   useEffect(() => {
     const controller = new AbortController();
     setLoading(true);
     
     fetch(url, { signal: controller.signal })
       .then(res => res.json())
       .then(data => setData(data))
       .catch(err => {
         if (err.name === 'AbortError') return;
         setError(err);
       })
       .finally(() => setLoading(false));
       
     return () => controller.abort();
   }, [url]);
   ```

3. **Debouncing pattern:**
   ```jsx
   useEffect(() => {
     const timer = setTimeout(() => {
       setDebouncedValue(value);
     }, 500);
     return () => clearTimeout(timer);
   }, [value]);
   ```

---

## 🔮 Tomorrow: Day 5 Preview

**Topics:**
- `useRef` (DOM access + stable values)
- `useMemo` and `useCallback` (performance)
- When NOT to use memoization
- Common hook mistakes

**What this unlocks:**
- Direct DOM manipulation
- Optimizing expensive calculations
- Preventing unnecessary re-renders
- Building performant apps

**Prep questions to think about:**
1. "What's the difference between useRef and useState?"
2. "When should you use useMemo?"
3. "What's the cost of premature optimization?"

---

## 💪 Self-Assessment

Before moving to Day 5, can you answer these confidently?

- [ ] Do I know when useEffect runs with different dependency arrays?
- [ ] Can I write a cleanup function for timers and fetch requests?
- [ ] Do I understand race conditions and how to prevent them?
- [ ] Can I fetch data with loading/error states?
- [ ] Do I know how to debounce user input?

If you checked all boxes, you're ready for Day 5! 🎉

If not, review the specific concept in `day4/lesson.md` or re-do the exercises.

---

## 🎯 Day 5 starts when you're ready!

**Location:** `day5/lesson.md`

Excellent progress! You now understand the foundation of React's side effects system. Day 5 will teach you performance optimization! 🚀
