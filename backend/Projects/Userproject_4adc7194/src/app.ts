import express, { Application, Request, Response, NextFunction } from 'express';
import { stripeService } from './services/stripe';
import { initRedis } from './services/redis';
import { initEmail } from './services/email';
import { config } from './config/env';

const app: Application = express();
const PORT = config.port;

// Middleware
app.use(express.json());
app.use(express.raw({ type: 'application/json' })); // For Stripe webhooks

// Initialize services on startup
const initServices = async () => {
  await initRedis();
  await initEmail();
};
initServices();

// Health check
app.get('/health', (req: Res, res: Response) => {
  res.status(200).json({ status: 'OK', services: 'Stripe, Redis, Email integrated' });
});

// Example Stripe endpoint
app.post('/create-payment-intent', async (req: Request, res: Response) => {
  try {
    const { amount, customerId } = req.body;
    const paymentIntent = await stripeService.createPaymentIntent(amount, 'usd', customerId);
    res.json({ clientSecret: paymentIntent.client_secret });
  } catch (error) {
    res.status(500).json({ error: 'Payment intent creation failed' });
  }
});

// Example Stripe webhook
app.post('/stripe/webhook', (req: Request, res: Response) => {
  const sig = req.headers['stripe-signature'] as string;
  let event;

  try {
    event = stripeService.verifyWebhook(sig, req.body);
  } catch (err) {
    res.status(400).send(`Webhook Error: ${err.message}`);
    return;
  }

  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      console.log('Payment succeeded:', event.data.object);
      // Integrate with Redis or email here if needed
      break;
    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  res.json({ received: true });
});

// Example Redis endpoint
app.get('/cache/:key', async (req: Request, res: Response) => {
  try {
    const value = await redisService.get(req.params.key);
    res.json({ value });
  } catch (error) {
    res.status(500).json({ error: 'Cache get failed' });
  }
});

app.post('/cache/:key', async (req: Request, res: Response) => {
  try {
    await redisService.set(req.params.key, req.body.value || '');
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Cache set failed' });
  }
});

// Example Email endpoint
app.post('/send-email', async (req: Request, res: Response) => {
  try {
    const { to, subject, html } = req.body;
    await emailService.sendEmail(to, subject, html);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Email send failed' });
  }
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export default app;