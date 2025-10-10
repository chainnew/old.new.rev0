import Stripe from 'stripe';
import { config } from '../config/env';

const stripe = new Stripe(config.stripe.secretKey, {
  apiVersion: '2023-10-16',
});

export const stripeService = {
  createCustomer: async (email: string, name?: string) => {
    try {
      const customer = await stripe.customers.create({ email, name });
      return customer;
    } catch (error) {
      console.error('Stripe customer creation error:', error);
      throw new Error('Failed to create customer');
    }
  },

  createPaymentIntent: async (amount: number, currency: string = 'usd', customerId?: string) => {
    try {
      const paymentIntent = await stripe.paymentIntents.create({
        amount,
        currency,
        customer: customerId,
        automatic_payment_methods: { enabled: true },
      });
      return paymentIntent;
    } catch (error) {
      console.error('Stripe payment intent creation error:', error);
      throw new Error('Failed to create payment intent');
    }
  },

  verifyWebhook: (signature: string, payload: Buffer) => {
    try {
      const event = stripe.webhooks.constructEvent(payload, signature, config.stripe.webhookSecret);
      return event;
    } catch (error) {
      console.error('Webhook signature verification failed:', error);
      throw new Error('Webhook verification failed');
    }
  },
};