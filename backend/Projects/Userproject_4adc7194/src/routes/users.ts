import { Router } from 'express';
import { createUserSchema, updateUserSchema, getUserSchema } from '../schemas/user';
import { validateRequest } from '../middleware/validate';

const router = Router();

// In-memory store for demo (replace with DB in production)
let users: any[] = [
  { id: '123e4567-e89b-12d3-a456-426614174000', name: 'John Doe', email: 'john@example.com', age: 30 },
];

// GET /api/users - Get all users
router.get('/', (req, res) => {
  res.json({ users });
});

// GET /api/users/:id - Get user by ID
router.get('/:id', validateRequest(getUserSchema), (req, res) => {
  const { id } = req.params;
  const user = users.find(u => u.id === id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json({ user });
});

// POST /api/users - Create user
router.post('/', validateRequest(createUserSchema), (req, res) => {
  const { name, email, age } = req.body;
  const newUser = {
    id: require('crypto').randomUUID(),
    name,
    email,
    age,
  };
  users.push(newUser);
  res.status(201).json({ user: newUser });
});

// PUT /api/users/:id - Update user
router.put('/:id', validateRequest(updateUserSchema), (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  const userIndex = users.findIndex(u => u.id === id);
  if (userIndex === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  users[userIndex] = { ...users[userIndex], ...updates };
  res.json({ user: users[userIndex] });
});

// DELETE /api/users/:id - Delete user
router.delete('/:id', validateRequest(getUserSchema), (req, res) => {
  const { id } = req.params;
  const userIndex = users.findIndex(u => u.id === id);
  if (userIndex === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  users.splice(userIndex, 1);
  res.status(204).send();
});

export default router;