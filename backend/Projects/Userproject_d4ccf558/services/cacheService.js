const redisClient = require('../lib/redis');

async function set(key, value, ttl = 3600) { // ttl in seconds, default 1 hour
  try {
    await redisClient.setEx(key, ttl, JSON.stringify(value));
  } catch (error) {
    console.error('Error setting cache:', error);
    throw error;
  }
}

async function get(key) {
  try {
    const data = await redisClient.get(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Error getting cache:', error);
    throw error;
  }
}

async function del(key) {
  try {
    await redisClient.del(key);
  } catch (error) {
    console.error('Error deleting cache:', error);
    throw error;
  }
}

module.exports = {
  set,
  get,
  del,
};