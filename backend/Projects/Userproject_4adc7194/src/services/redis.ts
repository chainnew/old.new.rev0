import { createClient, RedisClientType } from 'redis';
import { config } from '../config/env';

let redisClient: RedisClientType;

export const initRedis = async (): Promise<RedisClientType> => {
  if (!redisClient) {
    redisClient = createClient({
      url: config.redis.url,
    });

    redisClient.on('error', (err) => console.error('Redis Client Error', err));

    await redisClient.connect();
    console.log('Redis connected');
  }
  return redisClient;
};

export const redisService = {
  getClient: (): RedisClientType => {
    if (!redisClient) {
      throw new Error('Redis client not initialized');
    }
    return redisClient;
  },

  set: async (key: string, value: string, ttlSeconds?: number) => {
    const client = await initRedis();
    if (ttlSeconds) {
      await client.setEx(key, ttlSeconds, value);
    } else {
      await client.set(key, value);
    }
  },

  get: async (key: string) => {
    const client = await initRedis();
    return await client.get(key);
  },

  del: async (key: string) => {
    const client = await initRedis();
    await client.del(key);
  },
};