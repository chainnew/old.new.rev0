import nodemailer, { Transporter } from 'nodemailer';
import { SendMailOptions } from 'nodemailer';

interface EmailOptions extends SendMailOptions {
  to: string;
  subject: string;
  html?: string;
  text?: string;
}

const createTransporter = (): Transporter => {
  const transporter = nodemailer.createTransporter({
    host: process.env.EMAIL_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.EMAIL_PORT || '587', 10),
    secure: process.env.EMAIL_SECURE === 'true', // true for 465, false for other ports
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS,
    },
    tls: {
      rejectUnauthorized: false, // For production, ensure proper certs
    },
  });

  transporter.verify((error, success) => {
    if (error) {
      console.error('Email transporter verification failed:', error);
    } else {
      console.log('Email transporter is ready');
    }
  });

  return transporter;
};

const transporter: Transporter = createTransporter();

const sendEmail = async (options: EmailOptions): Promise<boolean> => {
  try {
    await transporter.sendMail({
      from: `"UserProject" <${process.env.EMAIL_USER}>`,
      ...options,
    });
    return true;
  } catch (error) {
    console.error('Failed to send email:', error);
    return false;
  }
};

export { transporter, sendEmail };
export type { EmailOptions };