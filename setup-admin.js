// Setup script to create default admin user
const { MongoClient } = require('mongodb');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'test_series_db';

async function setupAdmin() {
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    // Check if admin already exists
    const existingAdmin = await db.collection('users').findOne({ role: 'admin' });
    
    if (existingAdmin) {
      console.log('Admin user already exists:', existingAdmin.username);
      return;
    }
    
    // Create default admin user
    const hashedPassword = await bcrypt.hash('admin123', 12);
    const adminUser = {
      userId: uuidv4(),
      username: 'admin',
      password: hashedPassword,
      name: 'System Administrator',
      role: 'admin',
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    await db.collection('users').insertOne(adminUser);
    
    console.log('Default admin user created:');
    console.log('Username: admin');
    console.log('Password: admin123');
    console.log('Role: admin');
    
  } catch (error) {
    console.error('Error setting up admin:', error);
  } finally {
    await client.close();
  }
}

setupAdmin();