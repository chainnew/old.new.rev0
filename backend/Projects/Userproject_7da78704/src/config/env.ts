// Ensure these are loaded in your main app file, e.g., via dotenv
import dotenv from 'dotenv';

dotenv.config();

export const config = {
  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY,
  },
  redis: {
    url: process.env.REDIS_URL,
  },
  email: {
    host: process.env.EMAIL_HOST,
    port: process.env.EMAIL_PORT,
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
    secure: process.env.EMAIL_SECURE,
  },
};