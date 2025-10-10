const { stripeClient } = require('../lib/stripe');

async function createPaymentIntent(amount, currency = 'usd', metadata = {}) {
  try {
    const paymentIntent = await stripeClient.paymentIntents.create({
      amount,
      currency,
      metadata,
    });
    return paymentIntent;
  } catch (error) {
    console.error('Error creating payment intent:', error);
    throw error;
  }
}

async function confirmPaymentIntent(paymentIntentId) {
  try {
    const paymentIntent = await stripeClient.paymentIntents.confirm(paymentIntentId);
    return paymentIntent;
  } catch (error) {
    console.error('Error confirming payment intent:', error);
    throw error;
  }
}

module.exports = {
  createPaymentIntent,
  confirmPaymentIntent,
};