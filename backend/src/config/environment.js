import dotenv from 'dotenv';

const envResult = dotenv.config();
if (envResult.error && process.env.NODE_ENV !== 'test') {
  console.warn('Environment file not found. Falling back to process environment variables.');
}

export const environment = {
  port: parseInt(process.env.PORT, 10) || 4000,
  nodeEnv: process.env.NODE_ENV || 'development',
  corsOrigins: (process.env.CORS_ORIGINS || '').split(',').map(origin => origin.trim()).filter(Boolean),
};
