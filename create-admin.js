const { MongoClient } = require('mongodb');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
const dbName = process.env.DB_NAME || 'test_series_db';

async function createAdmin(username, password, name, email) {
  try {
    await client.connect();
    const db = client.db(dbName);

    // Check if user already exists
    const existingUser = await db.collection('users').findOne({ 
      $or: [{ username }, { email }] 
    });
    
    if (existingUser) {
      console.log('❌ User already exists with this username or email');
      return;
    }

    const userId = uuidv4();
    const hashedPassword = await bcrypt.hash(password, 12);

    const newAdmin = {
      userId,
      username,
      password: hashedPassword,
      name,
      email: email || null,
      role: 'admin',
      createdAt: new Date()
    };

    await db.collection('users').insertOne(newAdmin);
    console.log('✅ Admin account created successfully!');
    console.log(`Username: ${username}`);
    console.log(`Name: ${name}`);
    console.log(`Email: ${email || 'Not provided'}`);

  } catch (error) {
    console.error('❌ Error creating admin:', error);
  } finally {
    await client.close();
  }
}

// Get command line arguments
const args = process.argv.slice(2);
if (args.length < 3) {
  console.log('Usage: node create-admin.js <username> <password> <name> [email]');
  console.log('Example: node create-admin.js newadmin admin123 "John Doe" "john@example.com"');
  process.exit(1);
}

const [username, password, name, email] = args;
createAdmin(username, password, name, email);