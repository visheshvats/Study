# Day 1 Mini-Project: Personal Card Component

## 🎯 Goal
Build a reusable `PersonCard` component that displays information about a person.

**Time:** 30-60 minutes

---

## 📋 Requirements

Create a `PersonCard` component that:

1. Accepts the following props:
   - `name` (string)
   - `role` (string)
   - `bio` (string)
   - `imageUrl` (string, optional)

2. Displays:
   - Profile image (or placeholder if no imageUrl)
   - Name as heading
   - Role as subheading
   - Bio as paragraph

3. Styling:
   - Add basic CSS to make it look like a card
   - Border, padding, rounded corners
   - Center the image
   - Use clean typography

4. Usage in `App.jsx`:
   - Render 3 different PersonCard components
   - Each with different data (your choice)

---

## ✅ Acceptance Criteria

- [ ] PersonCard component is in its own file
- [ ] All 4 props are accepted and used
- [ ] Falls back to a placeholder if imageUrl is missing
- [ ] Card has visual styling (border, padding, etc.)
- [ ] App.jsx renders 3 different cards
- [ ] No console errors

---

## 🐛 Edge Cases to Handle

1. **No image provided:** Show a placeholder div with background color
2. **Long bio:** Text should wrap nicely (don't overflow)
3. **Empty name/role:** What happens? (Add a check or default)

---

## 📁 File Structure

```
day1/
  mini-project/
    PersonCard.jsx
    PersonCard.css
    App.jsx
    App.css
```

---

## 💡 Starter Code

**PersonCard.jsx:**
```jsx
function PersonCard({ name, role, bio, imageUrl }) {
  return (
    <div className="person-card">
      {/* Add image or placeholder here */}
      {/* Add name as <h2> */}
      {/* Add role as <h3> */}
      {/* Add bio as <p> */}
    </div>
  );
}

export default PersonCard;
```

**PersonCard.css:**
```css
.person-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  max-width: 300px;
  margin: 20px;
  /* Add more styles */
}

/* Add styles for image, headings, etc. */
```

**App.jsx:**
```jsx
import PersonCard from './PersonCard';
import './App.css';

function App() {
  return (
    <div className="app">
      <h1>Team Members</h1>
      {/* Render 3 PersonCard components with different data */}
    </div>
  );
}

export default App;
```

---

## 📋 Self-Review Checklist (Before Submitting)

- [ ] Does it run without errors?
- [ ] Did I handle the missing imageUrl case?
- [ ] Are all 3 cards displaying with different data?
- [ ] Is my code properly indented and readable?
- [ ] Can I explain why I structured it this way?

---

## 🎨 Bonus Challenges (Optional)

1. Add a `link` prop for a "View Profile" button
2. Add hover effects (scale up slightly on hover)
3. Make the card clickable (use `onClick` prop)
4. Add a "verified" badge if a `verified` prop is true

---

## 📤 Submission

When ready, paste your code here for review. I'll check for:
- ✅ Correct prop usage
- ✅ Clean component structure
- ✅ Edge case handling
- ✅ Code quality and best practices

**Remember:** Code quality matters as much as functionality in interviews!
