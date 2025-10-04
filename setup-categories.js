const { MongoClient } = require('mongodb');
const { v4: uuidv4 } = require('uuid');

const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
const dbName = process.env.DB_NAME || 'test_series_db';

async function setupCategories() {
  try {
    await client.connect();
    const db = client.db(dbName);

    // Check if categories already exist
    const existingCategories = await db.collection('categories').countDocuments();
    if (existingCategories > 0) {
      console.log('Categories already exist. Skipping setup.');
      return;
    }

    // Default categories
    const categories = [
      {
        categoryId: uuidv4(),
        name: 'JEE-Mains',
        description: 'Joint Entrance Examination - Main for engineering admissions',
        createdBy: 'system',
        createdAt: new Date()
      },
      {
        categoryId: uuidv4(),
        name: 'CUET PG',
        description: 'Common University Entrance Test - Post Graduate',
        createdBy: 'system',
        createdAt: new Date()
      },
      {
        categoryId: uuidv4(),
        name: 'NEET',
        description: 'National Eligibility cum Entrance Test for medical courses',
        createdBy: 'system',
        createdAt: new Date()
      },
      {
        categoryId: uuidv4(),
        name: 'GATE',
        description: 'Graduate Aptitude Test in Engineering',
        createdBy: 'system',
        createdAt: new Date()
      },
      {
        categoryId: uuidv4(),
        name: 'CAT',
        description: 'Common Admission Test for MBA programs',
        createdBy: 'system',
        createdAt: new Date()
      }
    ];

    await db.collection('categories').insertMany(categories);
    console.log('Default categories created successfully');

  } catch (error) {
    console.error('Error setting up categories:', error);
  } finally {
    await client.close();
  }
}

setupCategories();