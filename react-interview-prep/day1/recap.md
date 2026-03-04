# Day 1 Recap & Tomorrow's Prep

## 🎯 Day 1 Summary

Today you learned the three fundamental building blocks of React:

### 1. JSX
- ✅ HTML-like syntax in JavaScript
- ✅ Use `className` not `class`
- ✅ Close all tags (self-closing for single tags)
- ✅ Wrap adjacent elements in fragments `<>...</>`

### 2. Components
- ✅ Functions that return JSX
- ✅ Names MUST start with capital letters
- ✅ Reusable pieces of UI
- ✅ Export/import to use across files

### 3. Props
- ✅ Pass data from parent to child
- ✅ Read-only (cannot modify in child)
- ✅ Access via `props.name` or destructure `{ name }`
- ✅ Use curly braces for dynamic values

---

## 📊 What You Built Today

- ✅ Fixed broken JSX
- ✅ Created multiple components
- ✅ Passed props between components
- ✅ Built a PersonCard component with styling

---

## ⚠️ Common Mistakes You Avoided

1. ❌ Lowercase component names → ✅ Always capitalize
2. ❌ Modifying props → ✅ Props are read-only
3. ❌ Unclosed tags → ✅ Self-close single tags with `/>`
4. ❌ Forgetting curly braces → ✅ `{variable}` for interpolation

---

## 🧠 Key Interview Concepts Covered

### Question: "What are props in React?"
**Your answer should include:**
- Props = properties passed from parent to child
- Unidirectional flow (one-way: parent → child)
- Read-only, cannot be modified by child
- Example: `<Greeting name="Alice" />`

### Question: "Why must component names be capitalized?"
**Your answer:**
- React distinguishes components from HTML tags
- Lowercase = treated as HTML (e.g., `<div>`)
- Uppercase = treated as React component (e.g., `<MyComponent>`)

---

## 📝 What to Revise Tomorrow Morning (5 mins)

Before starting Day 2, quickly review:

1. **JSX syntax rules:**
   - `className` (not `class`)
   - Self-closing tags
   - Curly braces for JS expressions

2. **Component basics:**
   - Capital letter naming
   - Function that returns JSX
   - Export/import

3. **Props:**
   - How to pass them: `<Child name="value" />`
   - How to receive them: `function Child({ name })`
   - They are read-only

**Quick review:** Open `day1/lesson.md` and skim the examples (3 mins)

---

## 🔮 Tomorrow: Day 2 Preview

**Topics:**
- `useState` hook (managing component state)
- Rendering lists with `.map()`
- Keys and why they're important

**What this unlocks:**
- Making components interactive
- Displaying dynamic data
- Building a real Todo list

**Prep questions to think about:**
1. "What's the difference between props and state?"
2. "Why do we need keys when rendering lists?"

---

## 💪 Self-Assessment

Before moving to Day 2, can you answer these confidently?

- [ ] What is JSX and how is it different from HTML?
- [ ] Can I create a component and export it?
- [ ] Can I pass props and use them in a child?
- [ ] Do I know why component names must be capitalized?

If you checked all boxes, you're ready for Day 2! 🎉

If not, review the specific concept in `day1/lesson.md` before proceeding.

---

## 🎯 Day 2 starts when you're ready!

**Location:** `day2/lesson.md`

See you there! 🚀
