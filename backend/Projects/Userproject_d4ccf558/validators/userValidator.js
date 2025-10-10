const { z } = require('zod');

const userSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().min(0).max(150).optional(),
});

const createUserSchema = userSchema.omit({ id: true });
const updateUserSchema = userSchema.partial().refine((data) => {
  return Object.keys(data).some(key => ['name', 'email', 'age'].includes(key));
}, { message: 'At least one field must be provided for update' });

const validateRequest = (schema) => (req, res, next) => {
  try {
    schema.parse({
      body: req.body,
      params: req.params,
    });
    next();
  } catch (error) {
    res.status(400).json({ error: error.errors || 'Validation failed' });
  }
};

module.exports = {
  createUserSchema,
  updateUserSchema,
  validateRequest,
};