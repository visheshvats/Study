# Day 3: Events & Forms

## 📖 3-Minute Concept Lesson

### 1. Event Handling in React

**What it is:**  
React events are similar to DOM events, but with some differences. They use camelCase naming and you pass functions, not strings.

```jsx
// ❌ HTML way
<button onclick="handleClick()">Click</button>

// ✅ React way
<button onClick={handleClick}>Click</button>
```

**When to use:**  
Anytime you need to respond to user interactions: clicks, typing, form submissions, mouse movements, etc.

**Common mistakes:**
- ❌ Calling the function instead of passing it: `onClick={handleClick()}` → infinite loops!
- ❌ Using lowercase: `onclick` instead of `onClick`
- ❌ Forgetting `e.preventDefault()` for form submissions
- ❌ Not using arrow functions when you need to pass arguments

**Tiny example:**
```jsx
function Button() {
  const handleClick = (e) => {
    console.log('Button clicked!', e);
  };
  
  return <button onClick={handleClick}>Click me</button>;
}

// With inline arrow function
<button onClick={(e) => console.log('Clicked!')}>Click</button>

// Passing arguments
<button onClick={() => handleDelete(id)}>Delete</button>
```

**Common React Events:**
- `onClick` - any click
- `onChange` - input value changes
- `onSubmit` - form submission
- `onFocus` / `onBlur` - input focus
- `onKeyDown` / `onKeyPress` - keyboard
- `onMouseEnter` / `onMouseLeave` - hover

---

### 2. Controlled Components

**What it is:**  
A controlled component is an input whose value is controlled by React state. The state becomes the "single source of truth."

```jsx
function SearchBox() {
  const [query, setQuery] = useState('');
  
  return (
    <input
      type="text"
      value={query}           // ← Controlled by state
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}
```

**When to use:**  
ALWAYS for form inputs in React! This gives you full control over the input value.

**Common mistakes:**
- ❌ No onChange handler with value prop → input becomes read-only
- ❌ Forgetting `e.target.value` when getting input value
- ❌ Using uncontrolled components (value not from state)
- ❌ Not initializing state to empty string for inputs

**Tiny example:**
```jsx
// ❌ Uncontrolled - React doesn't know the value
<input type="text" />

// ✅ Controlled - State controls everything
const [name, setName] = useState('');
<input 
  type="text" 
  value={name} 
  onChange={(e) => setName(e.target.value)} 
/>
```

**Pattern for forms:**
```jsx
function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault(); // ← IMPORTANT!
    console.log({ email, password });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

---

### 3. Conditional Rendering

**What it is:**  
Showing or hiding elements based on conditions, using JavaScript logic in JSX.

**When to use:**  
Whenever UI needs to change based on state, props, or other conditions.

**Common patterns:**

**Pattern 1: Ternary Operator**
```jsx
{isLoggedIn ? <Dashboard /> : <LoginPage />}
```

**Pattern 2: Logical AND (&&)**
```jsx
{isLoggedIn && <WelcomeMessage />}
{error && <ErrorAlert message={error} />}
{items.length > 0 && <ItemList items={items} />}
```

**Pattern 3: Early Return**
```jsx
function UserProfile({ user }) {
  if (!user) return <p>Loading...</p>;
  if (user.blocked) return <p>Account blocked</p>;
  
  return <div>{user.name}</div>;
}
```

**Pattern 4: Variable Assignment**
```jsx
let content;
if (isLoading) {
  content = <Spinner />;
} else if (error) {
  content = <Error />;
} else {
  content = <Data />;
}

return <div>{content}</div>;
```

**Common mistakes:**
- ❌ Using `if` statements directly in JSX (doesn't work!)
- ❌ Returning `0` when using `&&`: `{count && <div>{count}</div>}` → shows "0" not nothing
- ❌ Complex ternaries that are hard to read
- ❌ Forgetting null check before accessing properties

**Tiny example:**
```jsx
function Greeting({ user }) {
  return (
    <div>
      {/* Ternary */}
      <h1>{user ? `Hello, ${user.name}` : 'Hello, Guest'}</h1>
      
      {/* Logical AND */}
      {user && <p>Email: {user.email}</p>}
      
      {/* NOT operator for opposite */}
      {!user && <button>Sign In</button>}
    </div>
  );
}
```

---

## 🔑 Key Takeaways

1. **Events** = Use camelCase, pass functions not calls
2. **Controlled Components** = State controls input value + onChange handler
3. **Conditional Rendering** = Ternary, &&, early return, or variables

---

## ⚠️ Interview Tips

**Common questions:**

> **"What's a controlled component?"**  
> **Answer:** A component whose form input values are controlled by React state. The value prop comes from state, and onChange updates the state. This makes React the single source of truth for the input value.

> **"How do you handle form submission in React?"**  
> **Answer:** Use the onSubmit event on the form, call e.preventDefault() to stop default browser behavior, then access form values from state (in controlled components).

> **"What's the difference between onClick={func} and onClick={func()}?"**  
> **Answer:** onClick={func} passes the function reference - it runs when clicked. onClick={func()} calls the function immediately during render, which causes infinite loops if it updates state.

---

## ✅ Self-Check Questions

Before moving to exercises:

1. Can I handle a button click event without causing infinite loops?
2. Do I know how to create a controlled input?
3. Can I conditionally render components using ternary and &&?
4. Do I know when to use e.preventDefault()?

If yes to all, proceed to exercises! 🎉

---

**Next:** `exercises/` folder for hands-on practice!
