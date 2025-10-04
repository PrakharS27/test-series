// Setup script to create custom admin user
const { MongoClient } = require('mongodb');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'test_series_db';

async function createCustomAdmin() {
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    // Check if this admin already exists
    const existingAdmin = await db.collection('users').findOne({ 
      username: 'prakharshivam0@gmail.com' 
    });
    
    if (existingAdmin) {
      console.log('Custom admin user already exists:', existingAdmin.username);
      return;
    }
    
    // Create custom admin user
    const hashedPassword = await bcrypt.hash('Admin!@Super@19892005', 12);
    const adminUser = {
      userId: uuidv4(),
      username: 'prakharshivam0@gmail.com',
      password: hashedPassword,
      name: 'Prakhar Shivam',
      role: 'admin',
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    await db.collection('users').insertOne(adminUser);
    
    console.log('Custom admin user created:');
    console.log('Username: prakharshivam0@gmail.com');
    console.log('Password: Admin!@Super@19892005');
    console.log('Role: admin');
    
  } catch (error) {
    console.error('Error setting up custom admin:', error);
  } finally {
    await client.close();
  }
}

createCustomAdmin();