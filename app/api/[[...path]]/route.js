import { NextRequest, NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

const client = new MongoClient(process.env.MONGO_URL);
const dbName = process.env.DB_NAME || 'test_series_db';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// Database connection
async function connectDB() {
  try {
    await client.connect();
    return client.db(dbName);
  } catch (error) {
    console.error('Database connection error:', error);
    throw error;
  }
}

// Middleware to verify JWT token
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

// Middleware to check role permissions
function hasPermission(userRole, requiredRoles) {
  return requiredRoles.includes(userRole);
}

// Helper function to get user from token
function getUserFromRequest(request) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '');
  if (!token) return null;
  return verifyToken(token);
}

async function handler(request, { params }) {
  const db = await connectDB();
  const path = params?.path || [];
  const method = request.method;
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };

  if (method === 'OPTIONS') {
    return new NextResponse(null, { status: 200, headers: corsHeaders });
  }

  try {
    // Authentication endpoints
    if (path[0] === 'auth') {
      if (path[1] === 'login' && method === 'POST') {
        const { username, password } = await request.json();
        
        // Find user in database
        const user = await db.collection('users').findOne({ username });
        if (!user) {
          return NextResponse.json({ error: 'Invalid credentials' }, { status: 401, headers: corsHeaders });
        }

        // Verify password
        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
          return NextResponse.json({ error: 'Invalid credentials' }, { status: 401, headers: corsHeaders });
        }

        // Generate JWT token
        const token = jwt.sign(
          { userId: user.userId, username: user.username, role: user.role },
          JWT_SECRET,
          { expiresIn: '24h' }
        );

        return NextResponse.json({
          token,
          user: { userId: user.userId, username: user.username, role: user.role, name: user.name }
        }, { headers: corsHeaders });
      }

      if (path[1] === 'register' && method === 'POST') {
        const { username, password, name, role } = await request.json();
        
        // Only allow student and teacher registration
        if (!['student', 'teacher'].includes(role)) {
          return NextResponse.json({ error: 'Invalid role' }, { status: 400, headers: corsHeaders });
        }

        // Check if user already exists
        const existingUser = await db.collection('users').findOne({ username });
        if (existingUser) {
          return NextResponse.json({ error: 'Username already exists' }, { status: 400, headers: corsHeaders });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 12);
        const userId = uuidv4();

        // Create user
        const user = {
          userId,
          username,
          password: hashedPassword,
          name,
          role,
          createdAt: new Date(),
          updatedAt: new Date()
        };

        await db.collection('users').insertOne(user);

        return NextResponse.json({ message: 'User created successfully' }, { headers: corsHeaders });
      }

      if (path[1] === 'me' && method === 'GET') {
        const user = getUserFromRequest(request);
        if (!user) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: corsHeaders });
        }
        
        const userData = await db.collection('users').findOne(
          { userId: user.userId },
          { projection: { password: 0, _id: 0 } }
        );
        
        return NextResponse.json(userData, { headers: corsHeaders });
      }
    }

    // Protected routes - require authentication
    const user = getUserFromRequest(request);
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: corsHeaders });
    }

    // Test Series endpoints
    if (path[0] === 'test-series') {
      if (method === 'GET' && !path[1]) {
        // Get all test series (filtered by role)
        let filter = {};
        if (user.role === 'teacher') {
          filter = { createdBy: user.userId };
        }
        
        const testSeries = await db.collection('testSeries')
          .find(filter, { projection: { _id: 0 } })
          .sort({ createdAt: -1 })
          .toArray();
        
        return NextResponse.json(testSeries, { headers: corsHeaders });
      }

      if (method === 'POST' && (user.role === 'admin' || user.role === 'teacher')) {
        const { title, description, category, duration, questions } = await request.json();
        
        const testSeriesId = uuidv4();
        const testSeries = {
          testSeriesId,
          title,
          description,
          category,
          duration, // in minutes
          questions: questions.map(q => ({ ...q, questionId: uuidv4() })),
          createdBy: user.userId,
          createdByName: user.name,
          createdAt: new Date(),
          updatedAt: new Date(),
          isActive: true
        };

        await db.collection('testSeries').insertOne(testSeries);
        
        return NextResponse.json({ message: 'Test series created successfully', testSeriesId }, { headers: corsHeaders });
      }

      if (method === 'PUT' && path[1] && (user.role === 'admin' || user.role === 'teacher')) {
        const testSeriesId = path[1];
        const updateData = await request.json();
        
        let filter = { testSeriesId };
        if (user.role === 'teacher') {
          filter.createdBy = user.userId;
        }
        
        await db.collection('testSeries').updateOne(
          filter,
          { $set: { ...updateData, updatedAt: new Date() } }
        );
        
        return NextResponse.json({ message: 'Test series updated successfully' }, { headers: corsHeaders });
      }

      if (method === 'DELETE' && path[1] && (user.role === 'admin' || user.role === 'teacher')) {
        const testSeriesId = path[1];
        
        let filter = { testSeriesId };
        if (user.role === 'teacher') {
          filter.createdBy = user.userId;
        }
        
        await db.collection('testSeries').deleteOne(filter);
        
        return NextResponse.json({ message: 'Test series deleted successfully' }, { headers: corsHeaders });
      }

      if (method === 'GET' && path[1]) {
        // Get single test series
        const testSeriesId = path[1];
        const testSeries = await db.collection('testSeries').findOne(
          { testSeriesId },
          { projection: { _id: 0 } }
        );
        
        if (!testSeries) {
          return NextResponse.json({ error: 'Test series not found' }, { status: 404, headers: corsHeaders });
        }
        
        return NextResponse.json(testSeries, { headers: corsHeaders });
      }
    }

    // Test Attempts endpoints
    if (path[0] === 'test-attempts') {
      if (method === 'POST' && user.role === 'student') {
        // Start a test attempt
        const { testSeriesId } = await request.json();
        
        // Check if test series exists
        const testSeries = await db.collection('testSeries').findOne({ testSeriesId });
        if (!testSeries) {
          return NextResponse.json({ error: 'Test series not found' }, { status: 404, headers: corsHeaders });
        }
        
        // Check if student already attempted this test
        const existingAttempt = await db.collection('testAttempts').findOne({
          testSeriesId,
          studentId: user.userId,
          status: 'completed'
        });
        
        if (existingAttempt) {
          return NextResponse.json({ error: 'Test already completed' }, { status: 400, headers: corsHeaders });
        }
        
        const attemptId = uuidv4();
        const startTime = new Date();
        const endTime = new Date(startTime.getTime() + (testSeries.duration * 60 * 1000));
        
        const attempt = {
          attemptId,
          testSeriesId,
          studentId: user.userId,
          studentName: user.name,
          startTime,
          endTime,
          status: 'in_progress',
          answers: {},
          score: 0,
          totalQuestions: testSeries.questions.length,
          createdAt: new Date()
        };
        
        await db.collection('testAttempts').insertOne(attempt);
        
        return NextResponse.json({ 
          attemptId, 
          endTime: endTime.toISOString(),
          totalQuestions: testSeries.questions.length
        }, { headers: corsHeaders });
      }

      if (method === 'PUT' && path[1] && user.role === 'student') {
        // Submit answer or complete test
        const attemptId = path[1];
        const { questionId, answer, action } = await request.json();
        
        const attempt = await db.collection('testAttempts').findOne({
          attemptId,
          studentId: user.userId
        });
        
        if (!attempt) {
          return NextResponse.json({ error: 'Test attempt not found' }, { status: 404, headers: corsHeaders });
        }
        
        if (attempt.status === 'completed') {
          return NextResponse.json({ error: 'Test already completed' }, { status: 400, headers: corsHeaders });
        }
        
        // Check if test time has expired
        if (new Date() > new Date(attempt.endTime)) {
          // Auto-submit the test
          const testSeries = await db.collection('testSeries').findOne({ testSeriesId: attempt.testSeriesId });
          let score = 0;
          
          for (const question of testSeries.questions) {
            if (attempt.answers[question.questionId] === question.correctAnswer) {
              score++;
            }
          }
          
          await db.collection('testAttempts').updateOne(
            { attemptId },
            { 
              $set: { 
                status: 'completed', 
                score,
                completedAt: new Date()
              } 
            }
          );
          
          return NextResponse.json({ 
            message: 'Test time expired and auto-submitted',
            score,
            totalQuestions: testSeries.questions.length
          }, { headers: corsHeaders });
        }
        
        if (action === 'submit_answer' && questionId && answer !== undefined) {
          // Update answer
          await db.collection('testAttempts').updateOne(
            { attemptId },
            { $set: { [`answers.${questionId}`]: answer } }
          );
          
          return NextResponse.json({ message: 'Answer saved' }, { headers: corsHeaders });
        }
        
        if (action === 'complete_test') {
          // Complete the test and calculate score
          const testSeries = await db.collection('testSeries').findOne({ testSeriesId: attempt.testSeriesId });
          let score = 0;
          
          for (const question of testSeries.questions) {
            if (attempt.answers[question.questionId] === question.correctAnswer) {
              score++;
            }
          }
          
          await db.collection('testAttempts').updateOne(
            { attemptId },
            { 
              $set: { 
                status: 'completed', 
                score,
                completedAt: new Date()
              } 
            }
          );
          
          return NextResponse.json({ 
            message: 'Test completed successfully',
            score,
            totalQuestions: testSeries.questions.length,
            percentage: Math.round((score / testSeries.questions.length) * 100)
          }, { headers: corsHeaders });
        }
      }

      if (method === 'GET' && path[1]) {
        // Get test attempt details
        const attemptId = path[1];
        const attempt = await db.collection('testAttempts').findOne(
          { attemptId },
          { projection: { _id: 0 } }
        );
        
        if (!attempt) {
          return NextResponse.json({ error: 'Test attempt not found' }, { status: 404, headers: corsHeaders });
        }
        
        // Only allow student to see their own attempts or teachers/admins to see attempts for their tests
        if (user.role === 'student' && attempt.studentId !== user.userId) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
        }
        
        return NextResponse.json(attempt, { headers: corsHeaders });
      }

      if (method === 'GET' && !path[1]) {
        // Get test attempts (for teachers to see results)
        let filter = {};
        
        if (user.role === 'student') {
          filter = { studentId: user.userId };
        } else if (user.role === 'teacher') {
          // Get attempts for teacher's test series
          const teacherTestSeries = await db.collection('testSeries')
            .find({ createdBy: user.userId })
            .toArray();
          const testSeriesIds = teacherTestSeries.map(ts => ts.testSeriesId);
          filter = { testSeriesId: { $in: testSeriesIds } };
        }
        
        const attempts = await db.collection('testAttempts')
          .find(filter, { projection: { _id: 0 } })
          .sort({ createdAt: -1 })
          .toArray();
        
        return NextResponse.json(attempts, { headers: corsHeaders });
      }
    }

    // Users endpoint (admin only)
    if (path[0] === 'users' && user.role === 'admin') {
      if (method === 'GET') {
        const users = await db.collection('users')
          .find({}, { projection: { password: 0, _id: 0 } })
          .sort({ createdAt: -1 })
          .toArray();
        
        return NextResponse.json(users, { headers: corsHeaders });
      }

      if (method === 'POST') {
        // Create admin user
        const { username, password, name } = await request.json();
        
        const existingUser = await db.collection('users').findOne({ username });
        if (existingUser) {
          return NextResponse.json({ error: 'Username already exists' }, { status: 400, headers: corsHeaders });
        }

        const hashedPassword = await bcrypt.hash(password, 12);
        const userId = uuidv4();

        const newUser = {
          userId,
          username,
          password: hashedPassword,
          name,
          role: 'admin',
          createdAt: new Date(),
          updatedAt: new Date()
        };

        await db.collection('users').insertOne(newUser);
        
        return NextResponse.json({ message: 'Admin user created successfully' }, { headers: corsHeaders });
      }
    }

    // Analytics endpoint
    if (path[0] === 'analytics') {
      if (user.role === 'student') {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403, headers: corsHeaders });
      }
      
      if (user.role === 'teacher') {
        // Get analytics for teacher's test series
        const teacherTestSeries = await db.collection('testSeries')
          .find({ createdBy: user.userId })
          .toArray();
        
        const testSeriesIds = teacherTestSeries.map(ts => ts.testSeriesId);
        
        const attempts = await db.collection('testAttempts')
          .find({ testSeriesId: { $in: testSeriesIds }, status: 'completed' })
          .toArray();
        
        const analytics = {
          totalTestSeries: teacherTestSeries.length,
          totalAttempts: attempts.length,
          averageScore: attempts.length > 0 ? attempts.reduce((sum, att) => sum + att.score, 0) / attempts.length : 0,
          testSeriesStats: teacherTestSeries.map(ts => {
            const tsAttempts = attempts.filter(att => att.testSeriesId === ts.testSeriesId);
            return {
              testSeriesId: ts.testSeriesId,
              title: ts.title,
              attempts: tsAttempts.length,
              averageScore: tsAttempts.length > 0 ? tsAttempts.reduce((sum, att) => sum + att.score, 0) / tsAttempts.length : 0
            };
          })
        };
        
        return NextResponse.json(analytics, { headers: corsHeaders });
      }

      if (user.role === 'admin') {
        // Get system-wide analytics
        const totalUsers = await db.collection('users').countDocuments();
        const totalTestSeries = await db.collection('testSeries').countDocuments();
        const totalAttempts = await db.collection('testAttempts').countDocuments({ status: 'completed' });
        
        const analytics = {
          totalUsers,
          totalTestSeries,
          totalAttempts
        };
        
        return NextResponse.json(analytics, { headers: corsHeaders });
      }
    }

    return NextResponse.json({ error: 'Endpoint not found' }, { status: 404, headers: corsHeaders });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500, headers: corsHeaders }
    );
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as OPTIONS };