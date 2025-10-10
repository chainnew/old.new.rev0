import nodemailer, { Transporter } from 'nodemailer';
import { config } from '../config/env';

let transporter: Transporter;

export const initEmail = async (): Promise<Transporter> => {
  if (!transporter) {
    transporter = nodemailer.createTransporter({
      service: config.email.service,
      auth: {
        user: config.email.user,
        pass: config.email.pass,
      },
    });

    // Test connection
    await transporter.verify();
    console.log('Email service connected');
  }
  return transporter;
};

export const emailService = {
  getTransporter: (): Transporter => {
    if (!transporter) {
      throw new Error('Email transporter not initialized');
    }
    return transporter;
  },

  sendEmail: async (to: string, subject: string, html: string, from?: string) => {
    const transporter = await initEmail();
    try {
      const info = await transporter.sendMail({
        from: from || config.email.user,
        to,
        subject,
        html,
      });
      console.log('Email sent:', info.messageId);
      return info;
    } catch (error) {
      console.error('Email sending error:', error);
      throw new Error('Failed to send email');
    }
  },
};