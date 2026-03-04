# Day 2 Interview Question

## ❓ Question

**Interviewer asks:**

> "I have this code that's supposed to display a list of users. It works, but I'm getting a warning in the console. What's wrong, and why does React care?"

```jsx
import { useState } from 'react';

function UserList() {
  const [users] = useState([
    { name: 'Alice', age: 25 },
    { name: 'Bob', age: 30 },
    { name: 'Charlie', age: 35 }
  ]);

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user, index) => (
          <li>
            {user.name} - {user.age} years old
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 📝 Your Task

Write your answer covering:
1. **What's the warning?** (What does the console say?)
2. **What's missing?** (Technical explanation)
3. **Why does React need it?** (Explain the purpose)
4. **How to fix it?** (Provide corrected code)
5. **Is using index as key OK here?** (When yes, when no)

---

## ✅ Evaluation Criteria

Your answer should cover:
- [ ] Identify the missing `key` prop
- [ ] Explain React's reconciliation process
- [ ] Show corrected code
- [ ] Discuss when index is acceptable as a key
- [ ] Mention what makes a good key (unique, stable)

---

## 🎯 Model Answer (Don't peek until you've tried!)

<details>
<summary>Click to reveal answer</summary>

### 1. The Warning:
```
Warning: Each child in a list should have a unique "key" prop.
```

### 2. What's Missing:
The `<li>` elements inside the `.map()` are missing the `key` prop.

### 3. Why React Needs Keys:
React uses keys to:
- **Track identity:** Know which items are the same across re-renders
- **Optimize performance:** Only update items that changed, not the entire list
- **Preserve state:** Maintain component state when list order changes
- **Prevent bugs:** Ensure correct rendering when items are added, removed, or reordered

Without keys, React falls back to using index positions, which breaks when:
- Items are reordered
- Items are added/removed from the middle
- Items have their own state (like input fields)

### 4. Fixed Code:

**Option 1: If users have unique IDs (BEST):**
```jsx
const [users] = useState([
  { id: 1, name: 'Alice', age: 25 },
  { id: 2, name: 'Bob', age: 30 },
  { id: 3, name: 'Charlie', age: 35 }
]);

return (
  <ul>
    {users.map(user => (
      <li key={user.id}>
        {user.name} - {user.age} years old
      </li>
    ))}
  </ul>
);
```

**Option 2: If no ID exists and list is static (ACCEPTABLE):**
```jsx
{users.map((user, index) => (
  <li key={index}>
    {user.name} - {user.age} years old
  </li>
))}
```

### 5. When is Index as Key OK?

**✅ OK to use index when:**
- List is static (never changes)
- Items are never reordered
- Items have no state
- You're just displaying read-only data

**❌ DON'T use index when:**
- List can be reordered (drag-and-drop, sorting)
- Items can be added/removed
- Items have state (checkboxes, inputs)
- Items can be filtered

**🏆 Best Practice:**
Always use a unique, stable identifier (like database ID) when available.

### Interview-Quality Summary:
"The code is missing keys on the mapped list items. React uses keys to efficiently track which items changed, were added, or removed during re-renders. While using the array index works for static lists, it's better to use unique IDs because indexes can cause bugs if the list is reordered or filtered. A good key should be unique and stable across re-renders."

</details>

---

## 💬 When You're Ready

Paste your answer, and I'll evaluate:
- Understanding of React's reconciliation
- Ability to explain WHY, not just WHAT
- Code correctness
- Interview communication skills

**Remember:** In interviews, showing you understand the "why" behind best practices is crucial!
