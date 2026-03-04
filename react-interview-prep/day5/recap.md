# Day 5 Recap & Tomorrow's Prep

## 🎯 Day 5 Summary

Today you learned advanced hooks for optimization and performance!

### 1. useRef
- ✅ Mutable value that persists across renders
- ✅ Doesn't trigger re-renders when changed
- ✅ Two uses: DOM access, stable values
- ✅ Access with `.current`

### 2. useMemo
- ✅ Memoizes expensive calculations
- ✅ Only recalculates when dependencies change
- ✅ **DON'T** use for simple operations
- ✅ Measure first, optimize second

### 3. useCallback
- ✅ Memoizes function references
- ✅ Prevents unnecessary child re-renders (with React.memo)
- ✅ **DON'T** use everywhere
- ✅ Only beneficial with memoized children

---

## 📊 What You Built Today

- ✅ DOM manipulation with useRef (focus, scroll, measure)
- ✅ Render counter and previous value tracker
- ✅ Optimization demo comparing with/without memoization
- ✅ **Product Search** with debouncing and optimizations

---

## ⚠️ Common Mistakes You Avoided

1. ❌ Using useRef for UI data → ✅ Use useState instead
2. ❌ Premature optimization → ✅ Measure first
3. ❌ useMemo everywhere → ✅ Only for expensive operations
4. ❌ useCallback without React.memo → ✅ No benefit
5. ❌ Forgetting `.current` → ✅ Always access refs with .current

---

## 🧠 Key Interview Concepts Covered

### Question: "What's the difference between useRef and useState?"
**Model answer:**
- **useState:** Changes trigger re-renders, use for data that affects UI
- **useRef:** Changes DON'T trigger re-renders, use for:
  - DOM references (focus, scroll)
  - Mutable values (timers, previous values, counters)
  - Any value that needs to persist but shouldn't cause re-renders

### Question: "When should you use useMemo?"
**Model answer:**
- **Only when:**
  - You've measured and found a performance problem
  - The calculation is genuinely expensive (> 1ms)
  - It runs frequently with same inputs
- **Don't use for:**
  - Simple calculations (a + b)
  - "Just in case" optimization
  - Before measuring performance
- **Quote:** "Premature optimization is the root of all evil"

### Question: "What's the difference between useMemo and useCallback?"
**Model answer:**
- **useMemo:** Returns a memoized VALUE
  ```jsx
  const value = useMemo(() => expensiveCalc(), [deps]);
  ```
- **useCallback:** Returns a memoized FUNCTION
  ```jsx
  const fn = useCallback(() => doSomething(), [deps]);
  ```
- **Equivalent:** `useCallback(fn, deps)` = `useMemo(() => fn, deps)`

### Question: "When does useCallback actually help performance?"
**Model answer:**
- **Only when:**
  - Child component is wrapped in React.memo
  - Function is in useEffect dependencies
  - Function is passed to expensive child
- **Doesn't help:**
  - Regular event handlers on DOM elements
  - Children without React.memo
  - Everywhere "just to be safe"
- **Adds overhead** in most cases!

---

## 📝 What to Revise Tomorrow Morning (5 mins)

Before starting Day 6, quickly review:

1. **useRef patterns:**
   ```jsx
   // DOM access
   const ref = useRef(null);
   <input ref={ref} />
   ref.current.focus();
   
   // Stable value
   const count = useRef(0);
   count.current += 1; // No re-render
   ```

2. **When to optimize:**
   ```jsx
   // ✅ Good use of useMemo
   const filtered = useMemo(() => 
     hugeArray.filter(expensive), 
   [hugeArray]);
   
   // ❌ Bad use of useMemo
   const sum = useMemo(() => a + b, [a, b]);
   ```

3. **useCallback pattern:**
   ```jsx
   const handleClick = useCallback(() => {
     setCount(prev => prev + 1); // Functional update
   }, []); // Empty deps = stable reference
   ```

---

## 🔮 Tomorrow: Day 6 Preview

**Topics:**
- Lifting state up
- Prop drilling vs Context API
- Composition patterns
- Building reusable components

**What this unlocks:**
- Sharing state between components
- Avoiding prop drilling
- Component communication
- Cleaner component architecture

**Prep questions to think about:**
1. "When should you lift state up?"
2. "What's prop drilling and when is it a problem?"
3. "When should you use Context API?"

---

## 💪 Self-Assessment

Before moving to Day 6, can you answer these confidently?

- [ ] Do I know when to use useRef vs useState?
- [ ] Can I access DOM elements with useRef?
- [ ] Do I understand when NOT to use useMemo?
- [ ] Can I explain the overhead of premature optimization?
- [ ] Do I know useCallback only helps with React.memo children?

If you checked all boxes, you're ready for Day 6! 🎉

If not, review the specific concept in `day5/lesson.md` or re-do the exercises.

---

## 🎯 Day 6 starts when you're ready!

**Location:** `day6/lesson.md`

Excellent! You now know how to optimize React apps. Day 6 will teach you component design patterns! 🚀
