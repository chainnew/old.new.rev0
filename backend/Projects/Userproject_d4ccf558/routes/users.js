const express = require('express');
const { createUserSchema, updateUserSchema, validateRequest } = require('../validators/userValidator');

const router = express.Router();
let users = []; // In-memory storage for demo; replace with DB in production
let nextId = 1;

// GET /api/users - List all users
router.get('/', (req, res) => {
  res.json(users);
});

// GET /api/users/:id - Get user by ID
router.get('/:id', (req, res) => {
  const user = users.find(u => u.id === req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

// POST /api/users - Create user
router.post('/', validateRequest(createUserSchema), (req, res) => {
  const { name, email, age } = req.body;
  const newUser = {
    id: nextId++.toString(),
    name,
    email,
    age,
  };
  users.push(newUser);
  res.status(201).json(newUser);
});

// PUT /api/users/:id - Update user
router.put('/:id', validateRequest(updateUserSchema), (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  users[index] = { ...users[index], ...req.body };
  res.json(users[index]);
});

// DELETE /api/users/:id - Delete user
router.delete('/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  users.splice(index, 1);
  res.status(204).send();
});

module.exports = router;