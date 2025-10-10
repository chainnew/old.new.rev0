const nodemailer = require('nodemailer');
const config = require('./config');

if (!config.email.user || !config.email.pass) {
  throw new Error('EMAIL_USER and EMAIL_PASS are required');
}

const transporter = nodemailer.createTransporter({
  service: config.email.service,
  auth: {
    user: config.email.user,
    pass: config.email.pass,
  },
});

transporter.verify((error, success) => {
  if (error) {
    console.error('Email transporter error:', error);
  } else {
    console.log('Email transporter ready');
  }
});

async function sendEmail(to, subject, html, text = '') {
  const mailOptions = {
    from: config.email.from,
    to,
    subject,
    html,
    text,
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    return info;
  } catch (error) {
    console.error('Error sending email:', error);
    throw error;
  }
}

module.exports = {
  sendEmail,
  transporter,
  config: config.email,
};