const { MongoClient } = require('mongodb');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
const dbName = process.env.DB_NAME || 'test_series_db';

async function setupSampleData() {
  try {
    await client.connect();
    const db = client.db(dbName);

    // Get categories
    const categories = await db.collection('categories').find({}).toArray();
    if (categories.length === 0) {
      console.log('No categories found. Please run setup-categories.js first.');
      return;
    }

    console.log('Found categories:', categories.map(c => c.name));

    // Create sample teachers
    const teachers = [
      {
        userId: uuidv4(),
        username: 'teacher_jee',
        password: await bcrypt.hash('teacher123', 12),
        name: 'Dr. Rajesh Kumar (JEE Expert)',
        email: 'rajesh.jee@example.com',
        role: 'teacher',
        photo: null,
        createdAt: new Date()
      },
      {
        userId: uuidv4(),
        username: 'teacher_neet',
        password: await bcrypt.hash('teacher123', 12),
        name: 'Dr. Priya Sharma (NEET Expert)',
        email: 'priya.neet@example.com',
        role: 'teacher',
        photo: null,
        createdAt: new Date()
      },
      {
        userId: uuidv4(),
        username: 'teacher_cuet',
        password: await bcrypt.hash('teacher123', 12),
        name: 'Prof. Amit Singh (CUET Expert)',
        email: 'amit.cuet@example.com',
        role: 'teacher',
        photo: null,
        createdAt: new Date()
      }
    ];

    // Check if teachers already exist
    const existingTeachers = await db.collection('users').find({
      username: { $in: teachers.map(t => t.username) }
    }).toArray();

    if (existingTeachers.length === 0) {
      await db.collection('users').insertMany(teachers);
      console.log('Sample teachers created successfully');
    } else {
      console.log('Sample teachers already exist');
    }

    // Get all teachers (existing + new)
    const allTeachers = await db.collection('users').find({ role: 'teacher' }).toArray();

    // Create test series for each category
    const testSeries = [];
    
    // JEE-Mains tests
    const jeeCategory = categories.find(c => c.name === 'JEE-Mains');
    if (jeeCategory) {
      testSeries.push({
        testSeriesId: uuidv4(),
        title: 'JEE Mains Physics Mock Test 1',
        description: 'Practice test for JEE Mains Physics - Mechanics and Thermodynamics',
        category: jeeCategory.categoryId,
        duration: 180,
        questions: [
          {
            questionId: uuidv4(),
            question: 'A ball is thrown vertically upward with initial velocity 20 m/s. What is the maximum height reached? (g = 10 m/s²)',
            options: ['10 m', '20 m', '30 m', '40 m'],
            correctAnswer: 1,
            explanation: 'Using v² = u² - 2gh, at maximum height v = 0, so h = u²/2g = 400/20 = 20 m'
          },
          {
            questionId: uuidv4(),
            question: 'In which process does the internal energy of an ideal gas remain constant?',
            options: ['Isothermal', 'Adiabatic', 'Isobaric', 'Isochoric'],
            correctAnswer: 0,
            explanation: 'In isothermal process, temperature remains constant, hence internal energy remains constant'
          }
        ],
        createdBy: teachers[0].userId,
        createdAt: new Date(),
        updatedAt: new Date()
      });

      testSeries.push({
        testSeriesId: uuidv4(),
        title: 'JEE Mains Mathematics Mock Test 1',
        description: 'Practice test for JEE Mains Mathematics - Algebra and Calculus',
        category: jeeCategory.categoryId,
        duration: 180,
        questions: [
          {
            questionId: uuidv4(),
            question: 'The derivative of sin(x²) is:',
            options: ['cos(x²)', '2x cos(x²)', '2x sin(x²)', 'x cos(x²)'],
            correctAnswer: 1,
            explanation: 'Using chain rule: d/dx[sin(x²)] = cos(x²) × 2x = 2x cos(x²)'
          }
        ],
        createdBy: teachers[0].userId,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }

    // NEET tests
    const neetCategory = categories.find(c => c.name === 'NEET');
    if (neetCategory) {
      testSeries.push({
        testSeriesId: uuidv4(),
        title: 'NEET Biology Mock Test 1',
        description: 'Practice test for NEET Biology - Cell Biology and Genetics',
        category: neetCategory.categoryId,
        duration: 180,
        questions: [
          {
            questionId: uuidv4(),
            question: 'Which organelle is known as the powerhouse of the cell?',
            options: ['Nucleus', 'Mitochondria', 'Ribosome', 'Golgi Apparatus'],
            correctAnswer: 1,
            explanation: 'Mitochondria produces ATP through cellular respiration, hence called powerhouse of cell'
          },
          {
            questionId: uuidv4(),
            question: 'The process by which DNA makes a copy of itself is called:',
            options: ['Transcription', 'Translation', 'Replication', 'Mutation'],
            correctAnswer: 2,
            explanation: 'DNA replication is the process of copying DNA to produce identical copies'
          }
        ],
        createdBy: teachers[1].userId,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }

    // CUET PG tests
    const cuetCategory = categories.find(c => c.name === 'CUET PG');
    if (cuetCategory) {
      testSeries.push({
        testSeriesId: uuidv4(),
        title: 'CUET PG General Awareness Test 1',
        description: 'Practice test for CUET PG - Current Affairs and General Knowledge',
        category: cuetCategory.categoryId,
        duration: 120,
        questions: [
          {
            questionId: uuidv4(),
            question: 'Who is the current President of India?',
            options: ['Ram Nath Kovind', 'Droupadi Murmu', 'Pranab Mukherjee', 'APJ Abdul Kalam'],
            correctAnswer: 1,
            explanation: 'Droupadi Murmu is the current President of India (as of 2024)'
          }
        ],
        createdBy: teachers[2].userId,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }

    // Check if test series already exist
    const existingTests = await db.collection('testSeries').find({
      title: { $in: testSeries.map(t => t.title) }
    }).toArray();

    if (existingTests.length === 0) {
      await db.collection('testSeries').insertMany(testSeries);
      console.log(`${testSeries.length} sample test series created successfully`);
    } else {
      console.log('Sample test series already exist');
    }

    console.log('\n✅ Sample data setup complete!');
    console.log('\nSample Teacher Accounts:');
    console.log('Username: teacher_jee, Password: teacher123 (JEE Expert)');
    console.log('Username: teacher_neet, Password: teacher123 (NEET Expert)');
    console.log('Username: teacher_cuet, Password: teacher123 (CUET Expert)');

  } catch (error) {
    console.error('Error setting up sample data:', error);
  } finally {
    await client.close();
  }
}

setupSampleData();