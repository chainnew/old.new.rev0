const { sendEmail } = require('../lib/email');

async function sendWelcomeEmail(userEmail, userName) {
  const subject = 'Welcome to UserProject!';
  const html = `
    <h1>Welcome, ${userName}!</h1>
    <p>Thank you for joining UserProject.</p>
  `;
  return sendEmail(userEmail, subject, html);
}

async function sendOrderConfirmationEmail(userEmail, orderDetails) {
  const subject = 'Order Confirmation';
  const html = `
    <h1>Order Confirmed!</h1>
    <p>Details: ${JSON.stringify(orderDetails)}</p>
  `;
  return sendEmail(userEmail, subject, html);
}

module.exports = {
  sendWelcomeEmail,
  sendOrderConfirmationEmail,
};