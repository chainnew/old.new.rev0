import express from 'express';
import { getAllUsers, getUserById, createUser, updateUser, deleteUser } from '../data/users';
import { createUserSchema, updateUserSchema, userIdSchema } from '../schemas/user';
import { validateBody, validateParams } from '../middleware/validation';

const router = express.Router();

router.get('/', (req, res) => {
  try {
    const users = getAllUsers();
    res.json({ data: users });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get(
  '/:id',
  validateParams(userIdSchema),
  (req, res) => {
    try {
      const user = getUserById(req.params.id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json({ data: user });
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

router.post('/', validateBody(createUserSchema), (req, res) => {
  try {
    const { name, email } = req.body;
    const newUser = createUser(name, email);
    res.status(201).json({ data: newUser });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put(
  '/:id',
  [validateParams(userIdSchema), validateBody(updateUserSchema)],
  (req, res) => {
    try {
      const { name, email } = req.body;
      const updatedUser = updateUser(req.params.id, name || '', email || '');
      if (!updatedUser) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json({ data: updatedUser });
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

router.delete(
  '/:id',
  validateParams(userIdSchema),
  (req, res) => {
    try {
      const deleted = deleteUser(req.params.id);
      if (!deleted) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

export default router;