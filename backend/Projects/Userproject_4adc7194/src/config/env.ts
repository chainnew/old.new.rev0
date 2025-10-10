import dotenv from 'dotenv';

dotenv.config();

export const config = {
  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY!,
    publishableKey: process.env.STRIPE_PUBLISHABLE_KEY!,
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET!,
  },
  redis: {
    url: process.env.REDIS_URL!,
  },
  email: {
    service: process.env.EMAIL_SERVICE!,
    user: process.env.EMAIL_USER!,
    pass: process.env.EMAIL_PASS!,
  },
  port: process.env.PORT || 3000,
};