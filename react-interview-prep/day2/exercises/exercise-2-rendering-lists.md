# Exercise 2: Rendering Lists (15 mins)

## 🎯 Goal
Use `.map()` to render a list of items from an array.

## 📝 Instructions

Create a `BookList.jsx` component that:
- Has an array of book objects (provided below)
- Renders each book as a card showing title and author
- Each book has a unique `id` for the key

**Data to use:**
```jsx
const books = [
  { id: 1, title: 'To Kill a Mockingbird', author: 'Harper Lee' },
  { id: 2, title: '1984', author: 'George Orwell' },
  { id: 3, title: 'The Great Gatsby', author: 'F. Scott Fitzgerald' },
  { id: 4, title: 'Pride and Prejudice', author: 'Jane Austen' }
];
```

**Starter code:**
```jsx
function BookList() {
  const books = [
    { id: 1, title: 'To Kill a Mockingbird', author: 'Harper Lee' },
    { id: 2, title: '1984', author: 'George Orwell' },
    { id: 3, title: 'The Great Gatsby', author: 'F. Scott Fitzgerald' },
    { id: 4, title: 'Pride and Prejudice', author: 'Jane Austen' }
  ];

  return (
    <div className="book-list">
      <h1>My Reading List</h1>
      {/* TODO: Map over books and render each one */}
    </div>
  );
}

export default BookList;
```

Expected output structure for each book:
```jsx
<div className="book-card" key={book.id}>
  <h3>{book.title}</h3>
  <p>by {book.author}</p>
</div>
```

## ✅ Acceptance Criteria
- [ ] All 4 books are rendered
- [ ] Each book shows title and author
- [ ] Each book has a unique `key` prop using `book.id`
- [ ] No console warnings about missing keys

## 🐛 Edge Cases
- What if the books array is empty? (Add a conditional message: "No books yet")
- What if a book is missing an author? (Display "Unknown Author")

## 📋 Self-Review Checklist
- [ ] Used `.map()` inside curly braces in JSX
- [ ] Each mapped item has a `key` prop
- [ ] Key uses `book.id` (not array index)
- [ ] Console shows no warnings

## 💡 Bonus Challenge

Add CSS to style the book cards:
```css
.book-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.book-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  width: 200px;
}

.book-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.book-card p {
  margin: 0;
  color: #666;
  font-style: italic;
}
```

---

**Time limit:** 15 minutes  
**Difficulty:** ⭐⭐☆

Once done, move to Exercise 3!
