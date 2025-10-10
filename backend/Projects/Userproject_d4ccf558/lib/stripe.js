const stripe = require('stripe');
const config = require('./config');

if (!config.stripe.secretKey) {
  throw new Error('STRIPE_SECRET_KEY is required');
}

const stripeClient = stripe(config.stripe.secretKey);

module.exports = {
  stripeClient,
  config: config.stripe,
};