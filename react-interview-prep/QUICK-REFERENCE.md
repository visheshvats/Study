# React Quick Reference - Days 1-2

## JSX Essentials

```jsx
// Variables in JSX
const name = "Alice";
<h1>Hello, {name}!</h1>

// Attributes
<img src={imageUrl} alt="description" className="my-class" />

// Conditional rendering
{isLoggedIn ? <Dashboard /> : <Login />}
{isLoggedIn && <Dashboard />}

// Fragments
<>
  <Header />
  <Main />
</>
```

## Components

```jsx
// Function component
function Welcome({ name }) {
  return <h1>Hello, {name}!</h1>;
}

// Using it
<Welcome name="Alice" />

// Export/Import
export default Welcome;
import Welcome from './Welcome';
```

## Props

```jsx
// Passing props
<UserCard 
  name="Alice" 
  age={25} 
  isAdmin={true}
  colors={['red', 'blue']}
/>

// Receiving props (destructured)
function UserCard({ name, age, isAdmin, colors }) {
  return <div>{name} - {age}</div>;
}

// With props object
function UserCard(props) {
  return <div>{props.name} - {props.age}</div>;
}

// Default props
function Button({ text = "Click me", variant = "primary" }) {
  return <button className={variant}>{text}</button>;
}
```

## State (useState)

```jsx
import { useState } from 'react';

// Creating state
const [count, setCount] = useState(0);
const [name, setName] = useState('Alice');
const [items, setItems] = useState([]);
const [user, setUser] = useState({ name: 'Bob', age: 30 });

// Updating state
setCount(count + 1);
setCount(prev => prev + 1); // Functional update

// Multiple state variables
function Form() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  // ...
}
```

## Lists & Keys

```jsx
// Basic list rendering
const items = ['Apple', 'Banana', 'Cherry'];

{items.map(item => (
  <li key={item}>{item}</li>
))}

// With objects (using ID as key)
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
];

{users.map(user => (
  <div key={user.id}>
    <h3>{user.name}</h3>
  </div>
))}

// With index (only for static lists)
{items.map((item, index) => (
  <li key={index}>{item}</li>
))}
```

## Event Handling

```jsx
// Click events
<button onClick={() => setCount(count + 1)}>
  Increment
</button>

// With handler function
function handleClick() {
  setCount(count + 1);
}
<button onClick={handleClick}>Increment</button>

// Input events
<input 
  value={text} 
  onChange={(e) => setText(e.target.value)}
/>

// Form submission
<form onSubmit={(e) => {
  e.preventDefault();
  // handle submit
}}>
```

## Common Patterns

### Controlled Input
```jsx
function SearchBox() {
  const [query, setQuery] = useState('');
  
  return (
    <input
      type="text"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

### Adding to Array
```jsx
// Add to end
setItems([...items, newItem]);

// Add to beginning
setItems([newItem, ...items]);

// Using functional update
setItems(prev => [...prev, newItem]);
```

### Conditional Rendering
```jsx
// Ternary
{isLoading ? <Spinner /> : <Content />}

// Logical AND
{error && <ErrorMessage />}
{items.length > 0 && <ItemList items={items} />}

// Early return
if (isLoading) return <Spinner />;
if (error) return <ErrorMessage />;
return <Content />;
```

### Toggle Boolean State
```jsx
const [isOpen, setIsOpen] = useState(false);

// Toggle
setIsOpen(!isOpen);

// Or with functional update
setIsOpen(prev => !prev);
```

## Common Mistakes to Avoid

```jsx
// ❌ Calling setState in render/onClick directly
<button onClick={setCount(count + 1)}>Bad</button>

// ✅ Wrap in arrow function
<button onClick={() => setCount(count + 1)}>Good</button>

// ❌ Mutating state
items.push(newItem);
setItems(items);

// ✅ Create new array
setItems([...items, newItem]);

// ❌ Missing key in list
{items.map(item => <li>{item}</li>)}

// ✅ Always add key
{items.map(item => <li key={item.id}>{item}</li>)}

// ❌ Lowercase component
function myComponent() { }

// ✅ Capitalize component names
function MyComponent() { }
```

## Interview Must-Knows

### Props vs State
| Props | State |
|-------|-------|
| Passed from parent | Owned by component |
| Read-only | Mutable (via setter) |
| Like function params | Like local variables |
| Cannot modify in child | Can update anytime |

### When to Use Index as Key
- ✅ Static list, never changes
- ✅ No reordering
- ❌ Dynamic lists
- ❌ Lists that can be sorted/filtered
- ❌ Items with state

### Why Keys Matter
1. Help React identify which items changed
2. Optimize rendering performance
3. Preserve component state correctly
4. Prevent bugs in dynamic lists

---

**Keep this handy while coding!** 📌
