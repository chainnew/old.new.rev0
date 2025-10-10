// Example integration in main app file (assuming Express.js setup)
import express from 'express';
import { connectRedis, disconnectRedis } from './services/redis.js';
import { config } from './config/env.js';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Initialize services on startup
const initServices = async (): Promise<void> => {
  if (config.redis.url) {
    await connectRedis();
  }
  // Stripe and email are initialized on import
};

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  await disconnectRedis();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully');
  await disconnectRedis();
  process.exit(0);
});

// Routes example (integrating services)
app.post('/create-payment-intent', async (req, res) => {
  try {
    const { amount } = req.body;
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: 'usd',
    });
    res.send({ clientSecret: paymentIntent.client_secret });
  } catch (error) {
    res.status(500).send({ error: (error as Error).message });
  }
});

app.post('/cache-user', async (req, res) => {
  try {
    const { userId, data } = req.body;
    await redisClient.set(userId, JSON.stringify(data), { EX: 3600 }); // 1 hour expiry
    res.send({ success: true });
  } catch (error) {
    res.status(500).send({ error: (error as Error).message });
  }
});

app.post('/send-email', async (req, res) => {
  try {
    const { to, subject, html, text } = req.body;
    const success = await sendEmail({ to, subject, html, text });
    if (success) {
      res.send({ success: true });
    } else {
      res.status(500).send({ error: 'Failed to send email' });
    }
  } catch (error) {
    res.status(500).send({ error: (error as Error).message });
  }
});

const startServer = async (): Promise<void> => {
  await initServices();
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
};

startServer().catch(console.error);