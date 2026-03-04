# Day 1 Interview Question

## ❓ Question

**Interviewer asks:**

> "Look at this code. What's wrong with it, and how would you fix it?"

```jsx
function welcome() {
  const user = "Alice";
  return <h1>Hello, user!</h1>
}

function App() {
  return <welcome />;
}
```

---

## 📝 Your Task

Write your answer covering:
1. **What's wrong?** (List all issues)
2. **Why is it wrong?** (Explain the rules)
3. **Fixed code** (Provide corrected version)

---

## ✅ Evaluation Criteria

Your answer should identify:
- [ ] Component naming issue
- [ ] JSX interpolation issue
- [ ] Provide fully corrected code

---

## 🎯 Model Answer (Don't peek until you've tried!)

<details>
<summary>Click to reveal answer</summary>

### Issues:

1. **Component name `welcome` should be `Welcome`**  
   - React components MUST start with a capital letter
   - Lowercase = HTML tag, Uppercase = React component

2. **`user` variable is not interpolated**  
   - `"user!"` is a literal string
   - Should be `{user}` to display the variable

### Fixed code:

```jsx
function Welcome() {
  const user = "Alice";
  return <h1>Hello, {user}!</h1>;
}

function App() {
  return <Welcome />;
}
```

### Key takeaway:
- Always capitalize component names
- Use `{variable}` for dynamic content in JSX

</details>

---

## 💬 When You're Ready

Paste your answer, and I'll evaluate it strictly and give you feedback on:
- Correctness
- Completeness
- Interview communication quality

**Remember:** In interviews, explain your reasoning, not just the fix!
