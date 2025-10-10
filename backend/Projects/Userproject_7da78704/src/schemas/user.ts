import { z } from 'zod';

export const createUserSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  email: z.string().email('Invalid email format'),
});

export const updateUserSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long').optional(),
  email: z.string().email('Invalid email format').optional(),
}).refine((data) => data.name || data.email, {
  message: 'At least one field must be provided for update',
});

export const userIdSchema = z.object({
  id: z.string().uuid('Invalid user ID format').or(z.string().min(1)),
});