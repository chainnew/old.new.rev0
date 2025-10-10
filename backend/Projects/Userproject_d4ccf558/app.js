// Example usage in a basic Express app (assuming Express is set up elsewhere)
const express = require('express');
const { createPaymentIntent } = require('./services/paymentService');
const { set, get } = require('./services/cacheService');
const { sendWelcomeEmail } = require('./services/emailService');

const app = express();
app.use(express.json());

// Example route using integrations
app.post('/create-payment', async (req, res) => {
  try {
    const { amount } = req.body;
    const paymentIntent = await createPaymentIntent(amount);
    res.json({ clientSecret: paymentIntent.client_secret });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/user/:id', async (req, res) => {
  const { id } = req.params;
  let user = await get(`user:${id}`);
  if (!user) {
    // Simulate fetching from DB
    user = { id, name: 'John Doe', email: 'john@example.com' };
    await set(`user:${id}`, user);
    await sendWelcomeEmail(user.email, user.name);
  }
  res.json(user);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});