# Day 1: React Fundamentals I

## 📖 3-Minute Concept Lesson

### 1. JSX (JavaScript XML)

**What it is:**  
JSX is a syntax extension for JavaScript that looks like HTML but lives inside your JavaScript code. It lets you describe UI in a familiar way.

```jsx
const element = <h1>Hello, React!</h1>;
```

**When to use:**  
Every time you write React components! JSX makes your code readable and declarative.

**Common mistakes:**
- ❌ Using `class` instead of `className`
- ❌ Forgetting to close self-closing tags: `<img>` → `<img />`
- ❌ Not wrapping adjacent elements in a parent (use `<>...</>` or `<div>`)

**Tiny example:**
```jsx
// ❌ Wrong
const wrong = <h1>Hello<h2>World</h2>;

// ✅ Correct
const correct = (
  <>
    <h1>Hello</h1>
    <h2>World</h2>
  </>
);
```

---

### 2. Components

**What it is:**  
Components are reusable pieces of UI. Think of them as JavaScript functions that return JSX.

```jsx
function Welcome() {
  return <h1>Welcome to React!</h1>;
}
```

**When to use:**  
Break your UI into small, focused components. One component = one responsibility.

**Common mistakes:**
- ❌ Component names must start with a capital letter: `welcome` → `Welcome`
- ❌ Forgetting to `return` JSX
- ❌ Making components too big (do one thing well)

**Tiny example:**
```jsx
// Component definition
function Greeting() {
  return <h1>Hello!</h1>;
}

// Using it
function App() {
  return (
    <div>
      <Greeting />
      <Greeting />
    </div>
  );
}
```

---

### 3. Props

**What it is:**  
Props (short for "properties") are how you pass data FROM a parent component TO a child component. They're like function arguments.

```jsx
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// Usage
<Greeting name="Alice" />
```

**When to use:**  
Whenever a child component needs data from its parent. Props flow ONE WAY: parent → child.

**Common mistakes:**
- ❌ Trying to modify props inside the child (`props.name = "Bob"` → NO!)
- ❌ Forgetting curly braces for dynamic values: `name={userName}` not `name="userName"`
- ❌ Not destructuring: `props.name` works, but `{ name }` is cleaner

**Tiny example:**
```jsx
// Destructuring props (best practice)
function UserCard({ name, age }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>Age: {age}</p>
    </div>
  );
}

// Usage
<UserCard name="Bob" age={25} />
```

---

## 🔑 Key Takeaways

1. **JSX** = HTML-like syntax in JavaScript
2. **Components** = Reusable UI functions (capital letter names!)
3. **Props** = Data passed parent → child (read-only!)

---

## ⚠️ Interview Tip

Interviewers love asking:
> "Can you modify props in a component?"  

**Answer:** No! Props are **read-only**. If you need to change data, use **state** (we'll learn tomorrow).

---

## ✅ Self-Check Questions

Before moving to exercises, ask yourself:

1. Can I explain what JSX is in one sentence?
2. Do I know why component names must be capitalized?
3. Can I pass a prop and use it inside a child component?

If you answered "yes" to all three, proceed to exercises! 🎉

---

**Next:** `exercises/` folder for hands-on practice!
