# Day 2 Mini-Project: Dynamic Todo List

## 🎯 Goal
Build a functional Todo List where users can add new items and see them displayed dynamically.

**Time:** 30-60 minutes

---

## 📋 Requirements

Create a Todo List application with:

1. **State management:**
   - Array of todo items (each with id, text, completed status)
   - Input field value for new todos

2. **Core functionality:**
   - Input field to type new todos
   - "Add" button to add todos to the list
   - Display all todos in a list
   - Each todo shows its text

3. **Data structure:**
```js
{
  id: 1,
  text: 'Learn React',
  completed: false
}
```

4. **User experience:**
   - Clear input field after adding a todo
   - Prevent adding empty todos
   - Display count of total todos

---

## ✅ Acceptance Criteria

- [ ] Can add new todos via input + button
- [ ] Each todo has a unique ID (use Date.now() or counter)
- [ ] All todos are displayed with proper keys
- [ ] Input clears after adding a todo
- [ ] Empty todos cannot be added
- [ ] Shows total todo count
- [ ] No console errors or warnings

---

## 🐛 Edge Cases to Handle

1. **Empty input:** Don't add if input is empty or just whitespace
2. **Whitespace:** Trim input before adding
3. **No todos yet:** Show "No todos yet!" message
4. **Enter key:** Allow adding todo by pressing Enter (not just clicking button)

---

## 📁 File Structure

```
day2/
  mini-project/
    TodoList.jsx
    TodoList.css
    App.jsx
```

---

## 💡 Starter Code

**TodoList.jsx:**
```jsx
import { useState } from 'react';
import './TodoList.css';

function TodoList() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const handleAddTodo = () => {
    // TODO: Implement add logic
    // 1. Check if input is not empty (after trim)
    // 2. Create new todo object with unique id
    // 3. Add to todos array
    // 4. Clear input field
  };

  const handleInputChange = (e) => {
    // TODO: Update inputValue state
  };

  const handleKeyPress = (e) => {
    // TODO: Add todo when Enter key is pressed
  };

  return (
    <div className="todo-container">
      <h1>My Todo List</h1>
      
      {/* Input Section */}
      <div className="input-section">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Enter a new todo..."
          className="todo-input"
        />
        <button onClick={handleAddTodo} className="add-button">
          Add
        </button>
      </div>

      {/* Stats */}
      <p className="todo-count">Total todos: {todos.length}</p>

      {/* Todo List */}
      <ul className="todo-list">
        {todos.length === 0 ? (
          <p className="empty-message">No todos yet! Add one above.</p>
        ) : (
          todos.map(todo => (
            <li key={todo.id} className="todo-item">
              {todo.text}
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default TodoList;
```

**TodoList.css:**
```css
.todo-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.todo-input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 4px;
}

.todo-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.add-button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-button:hover {
  background-color: #45a049;
}

.add-button:active {
  transform: scale(0.98);
}

.todo-count {
  text-align: center;
  color: #666;
  margin-bottom: 20px;
}

.todo-list {
  list-style: none;
  padding: 0;
}

.todo-item {
  background-color: #f9f9f9;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 4px;
  border-left: 4px solid #4CAF50;
}

.empty-message {
  text-align: center;
  color: #999;
  font-style: italic;
}
```

**App.jsx:**
```jsx
import TodoList from './TodoList';

function App() {
  return (
    <div className="App">
      <TodoList />
    </div>
  );
}

export default App;
```

---

## 📋 Implementation Checklist

Before submitting, verify:

- [ ] `useState` is imported
- [ ] `todos` state is an array
- [ ] `inputValue` state tracks the input
- [ ] `handleAddTodo` creates new todo with unique ID
- [ ] Input is trimmed and checked for empty/whitespace
- [ ] Input is cleared after adding (`setInputValue('')`)
- [ ] Todos use `.map()` with proper keys
- [ ] Key uses `todo.id`, not array index
- [ ] Enter key works to add todos
- [ ] Empty state message shows when no todos
- [ ] No console warnings

---

## 🎨 Bonus Challenges (Optional)

1. **Delete functionality:**
   - Add a delete button (❌) next to each todo
   - Remove todo from array when clicked

2. **Toggle completion:**
   - Add checkbox to mark todos as complete
   - Strike through completed todos

3. **Edit functionality:**
   - Double-click to edit a todo
   - Save changes on blur or Enter

4. **Persist data:**
   - Save todos to localStorage
   - Load saved todos on mount

---

## 💡 Hints

**Adding a new todo:**
```jsx
const newTodo = {
  id: Date.now(), // Simple unique ID
  text: inputValue.trim(),
  completed: false
};
setTodos([...todos, newTodo]); // Add to end
// OR
setTodos([newTodo, ...todos]); // Add to beginning
```

**Checking for Enter key:**
```jsx
const handleKeyPress = (e) => {
  if (e.key === 'Enter') {
    handleAddTodo();
  }
};
```

**Preventing empty todos:**
```jsx
if (inputValue.trim() === '') {
  return; // Exit early, don't add
}
```

---

## 📤 Submission

When ready, paste your code for review. I'll check:
- ✅ State management correctness
- ✅ Proper use of keys in lists
- ✅ Edge case handling
- ✅ Code quality and organization
- ✅ User experience (does it feel good to use?)

**Remember:** Clean, readable code is as important as working code in interviews!
