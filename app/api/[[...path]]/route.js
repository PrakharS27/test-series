import { NextRequest, NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

const client = new MongoClient(process.env.MONGO_URL);
const dbName = process.env.DB_NAME || 'test_series_db';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// Temporary email domains to block
const TEMP_EMAIL_DOMAINS = [
  '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 'tempmail.org',
  'throwaway.email', '0-mail.com', '10mail.org', '20minutemail.com',
  'burnermail.io', 'emailondeck.com', 'fakeinbox.com', 'guerrillamailblock.com',
  'harakirimail.com', 'mailnesia.com', 'sharklasers.com', 'spamgourmet.com',
  'temp-mail.org', 'tempinbox.com', 'trashmail.com', 'yopmail.com'
];

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

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// Main handler function
async function handler(request) {
  const { method } = request;
  const url = new URL(request.url);
  const path = url.pathname.split('/').filter(Boolean).slice(1); // Remove 'api' from path

  // Handle CORS preflight
  if (method === 'OPTIONS') {
    return new NextResponse(null, { status: 200, headers: corsHeaders });
  }

  try {
    const db = await connectDB();

    // Authentication routes
    if (path[0] === 'auth') {
      if (path[1] === 'login' && method === 'POST') {
        const { username, password } = await request.json();
        
        const user = await db.collection('users').findOne({ username });
        if (!user || !await bcrypt.compare(password, user.password)) {
          return NextResponse.json({ error: 'Invalid credentials' }, { status: 401, headers: corsHeaders });
        }

        const token = jwt.sign(
          { userId: user.userId, username: user.username, role: user.role },
          JWT_SECRET,
          { expiresIn: '24h' }
        );

        return NextResponse.json({ token, user: { userId: user.userId, username: user.username, role: user.role, name: user.name, selectedCategory: user.selectedCategory, selectedTeacher: user.selectedTeacher } }, { headers: corsHeaders });
      }

      if (path[1] === 'register' && method === 'POST') {
        const { username, password, name, role, email, phone, selectedCategory, selectedTeacher } = await request.json();

        // Check if user exists
        const existingUser = await db.collection('users').findOne({ 
          $or: [{ username }, { email }] 
        });
        if (existingUser) {
          return NextResponse.json({ error: 'User already exists' }, { status: 400, headers: corsHeaders });
        }

        // Block temporary email domains
        if (email) {
          const emailDomain = email.split('@')[1]?.toLowerCase();
          if (TEMP_EMAIL_DOMAINS.includes(emailDomain)) {
            return NextResponse.json({ error: 'Temporary email addresses are not allowed' }, { status: 400, headers: corsHeaders });
          }
        }

        const userId = uuidv4();
        const hashedPassword = await bcrypt.hash(password, 12);

        const newUser = {
          userId,
          username,
          password: hashedPassword,
          name,
          role: role || 'student',
          email: email || null,
          phone: phone || null,
          selectedCategory: selectedCategory || null,
          selectedTeacher: selectedTeacher || null,
          photo: null,
          createdAt: new Date()
        };

        await db.collection('users').insertOne(newUser);

        const token = jwt.sign(
          { userId, username, role: newUser.role },
          JWT_SECRET,
          { expiresIn: '24h' }
        );

        return NextResponse.json({ 
          token, 
          user: { userId, username, role: newUser.role, name, selectedCategory, selectedTeacher } 
        }, { headers: corsHeaders });
      }

      if (path[1] === 'forgot-password' && method === 'POST') {
        const { email } = await request.json();
        
        const user = await db.collection('users').findOne({ email });
        if (!user) {
          return NextResponse.json({ error: 'User not found with this email' }, { status: 404, headers: corsHeaders });
        }

        // Generate reset token
        const resetToken = uuidv4();
        const resetTokenExpiry = new Date(Date.now() + 3600000); // 1 hour

        await db.collection('users').updateOne(
          { userId: user.userId },
          { 
            $set: { 
              resetToken,
              resetTokenExpiry 
            } 
          }
        );

        // In a real app, send email here
        // For now, return the reset token for testing
        return NextResponse.json({ 
          message: 'Password reset link sent to your email',
          resetToken // Remove this in production
        }, { headers: corsHeaders });
      }

      if (path[1] === 'reset-password' && method === 'POST') {
        const { resetToken, newPassword } = await request.json();
        
        const user = await db.collection('users').findOne({ 
          resetToken,
          resetTokenExpiry: { $gt: new Date() }
        });

        if (!user) {
          return NextResponse.json({ error: 'Invalid or expired reset token' }, { status: 400, headers: corsHeaders });
        }

        const hashedPassword = await bcrypt.hash(newPassword, 12);

        await db.collection('users').updateOne(
          { userId: user.userId },
          { 
            $set: { 
              password: hashedPassword 
            },
            $unset: { 
              resetToken: "",
              resetTokenExpiry: "" 
            }
          }
        );

        return NextResponse.json({ message: 'Password reset successfully' }, { headers: corsHeaders });
      }

      if (path[1] === 'profile' && method === 'GET') {
        const user = getUserFromRequest(request);
        if (!user) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: corsHeaders });
        }

        const userProfile = await db.collection('users').findOne(
          { userId: user.userId },
          { projection: { password: 0, resetToken: 0, resetTokenExpiry: 0 } }
        );

        return NextResponse.json(userProfile, { headers: corsHeaders });
      }

      if (path[1] === 'profile' && method === 'PUT') {
        const user = getUserFromRequest(request);
        if (!user) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: corsHeaders });
        }

        const updates = await request.json();
        delete updates.password; // Don't allow password updates here
        delete updates.role; // Don't allow role changes

        await db.collection('users').updateOne(
          { userId: user.userId },
          { $set: updates }
        );

        return NextResponse.json({ message: 'Profile updated successfully' }, { headers: corsHeaders });
      }
    }

    // Categories routes
    if (path[0] === 'categories') {
      if (method === 'GET') {
        const { withTeachers } = Object.fromEntries(url.searchParams);
        
        if (withTeachers === 'true') {
          // Get categories with teachers who have tests in each category
          const pipeline = [
            {
              $lookup: {
                from: 'testSeries',
                localField: 'categoryId',
                foreignField: 'category',
                as: 'testSeries'
              }
            },
            {
              $unwind: {
                path: '$testSeries',
                preserveNullAndEmptyArrays: false
              }
            },
            {
              $lookup: {
                from: 'users',
                localField: 'testSeries.createdBy',
                foreignField: 'userId',
                as: 'teacher'
              }
            },
            {
              $unwind: '$teacher'
            },
            {
              $group: {
                _id: '$_id',
                categoryId: { $first: '$categoryId' },
                name: { $first: '$name' },
                description: { $first: '$description' },
                teachers: {
                  $addToSet: {
                    userId: '$teacher.userId',
                    name: '$teacher.name',
                    photo: '$teacher.photo',
                    rating: '$teacher.rating',
                    experience: '$teacher.experience'
                  }
                }
              }
            }
          ];
          
          const categoriesWithTeachers = await db.collection('categories').aggregate(pipeline).toArray();
          return NextResponse.json(categoriesWithTeachers, { headers: corsHeaders });
        } else {
          const categories = await db.collection('categories').find({}).toArray();
          return NextResponse.json(categories, { headers: corsHeaders });
        }
      }

      if (method === 'POST') {
        const user = getUserFromRequest(request);
        if (!user || !hasPermission(user.role, ['admin'])) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
        }

        const { name, description } = await request.json();
        const categoryId = uuidv4();

        const category = {
          categoryId,
          name,
          description: description || '',
          createdBy: user.userId,
          createdAt: new Date()
        };

        await db.collection('categories').insertOne(category);
        return NextResponse.json(category, { headers: corsHeaders });
      }

      if (method === 'DELETE' && path[1]) {
        const user = getUserFromRequest(request);
        if (!user || !hasPermission(user.role, ['admin'])) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
        }

        await db.collection('categories').deleteOne({ categoryId: path[1] });
        return NextResponse.json({ message: 'Category deleted successfully' }, { headers: corsHeaders });
      }
    }

    // Teachers by category route
    if (path[0] === 'teachers' && method === 'GET') {
      const { category } = Object.fromEntries(url.searchParams);
      
      // Always return all teachers - students can choose any teacher
      // Category filtering will be applied when viewing test series
      const teachers = await db.collection('users').find(
        { role: 'teacher' },
        { projection: { password: 0, resetToken: 0, resetTokenExpiry: 0 } }
      ).toArray();

      return NextResponse.json(teachers, { headers: corsHeaders });
    }

    // File upload route for teacher photos
    if (path[0] === 'upload' && path[1] === 'photo' && method === 'POST') {
      const user = getUserFromRequest(request);
      if (!user || !hasPermission(user.role, ['teacher', 'admin'])) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
      }

      try {
        const formData = await request.formData();
        const file = formData.get('photo');
        
        if (!file) {
          return NextResponse.json({ error: 'No file uploaded' }, { status: 400, headers: corsHeaders });
        }

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!validTypes.includes(file.type)) {
          return NextResponse.json({ error: 'Invalid file type. Only JPEG, PNG, and GIF are allowed.' }, { status: 400, headers: corsHeaders });
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
          return NextResponse.json({ error: 'File too large. Maximum size is 5MB.' }, { status: 400, headers: corsHeaders });
        }

        // Convert file to base64 for storage
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);
        const base64 = buffer.toString('base64');
        const photoData = `data:${file.type};base64,${base64}`;

        // Update user photo
        await db.collection('users').updateOne(
          { userId: user.userId },
          { $set: { photo: photoData } }
        );

        return NextResponse.json({ 
          message: 'Photo uploaded successfully',
          photoUrl: photoData 
        }, { headers: corsHeaders });

      } catch (error) {
        console.error('Photo upload error:', error);
        return NextResponse.json({ error: 'Failed to upload photo' }, { status: 500, headers: corsHeaders });
      }
    }

    // CSV bulk upload route
    if (path[0] === 'upload' && path[1] === 'csv' && method === 'POST') {
      const user = getUserFromRequest(request);
      if (!user || !hasPermission(user.role, ['teacher', 'admin'])) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
      }

      try {
        const formData = await request.formData();
        const file = formData.get('csv');
        const testSeriesId = formData.get('testSeriesId');
        
        if (!file || !testSeriesId) {
          return NextResponse.json({ error: 'CSV file and test series ID required' }, { status: 400, headers: corsHeaders });
        }

        // Validate file type
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
          return NextResponse.json({ error: 'Invalid file type. Only CSV files are allowed.' }, { status: 400, headers: corsHeaders });
        }

        const csvText = await file.text();
        const lines = csvText.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
          return NextResponse.json({ error: 'CSV must have at least a header row and one question' }, { status: 400, headers: corsHeaders });
        }

        // Skip header row
        const questions = [];
        for (let i = 1; i < lines.length; i++) {
          const columns = lines[i].split(',').map(col => col.trim().replace(/"/g, ''));
          
          if (columns.length >= 7) {
            const questionId = uuidv4();
            questions.push({
              questionId,
              question: columns[0],
              options: [columns[1], columns[2], columns[3], columns[4]],
              correctAnswer: parseInt(columns[5]) - 1, // Convert to 0-based index
              explanation: columns[6] || ''
            });
          }
        }

        if (questions.length === 0) {
          return NextResponse.json({ error: 'No valid questions found in CSV' }, { status: 400, headers: corsHeaders });
        }

        // Update test series with new questions
        await db.collection('testSeries').updateOne(
          { testSeriesId, createdBy: user.userId },
          { 
            $set: { 
              questions,
              updatedAt: new Date()
            } 
          }
        );

        return NextResponse.json({ 
          message: `Successfully uploaded ${questions.length} questions`,
          questionsCount: questions.length 
        }, { headers: corsHeaders });

      } catch (error) {
        console.error('CSV upload error:', error);
        return NextResponse.json({ error: 'Failed to process CSV file' }, { status: 500, headers: corsHeaders });
      }
    }

    // Test Series routes
    if (path[0] === 'test-series') {
      const user = getUserFromRequest(request);

      if (method === 'GET') {
        let query = {};
        const { category, teacher, includeUnpublished, preview } = Object.fromEntries(url.searchParams);
        
        if (user?.role === 'student') {
          // Students see ALL published test series from ALL teachers
          query.status = { $ne: 'draft' }; // Only published tests
          // Allow filtering by URL parameters
          if (category) query.category = category;
          if (teacher) query.createdBy = teacher;
        } else if (user?.role === 'teacher') {
          if (preview === 'true') {
            // Teacher preview - show specific test with full questions
            query.createdBy = user.userId;
          } else {
            query.createdBy = user.userId;
            // Teachers can see their drafts by default - they need to see their own work
            // Only hide drafts if explicitly specified to show only published
            if (includeUnpublished === 'false') {
              query.status = { $ne: 'draft' };
            }
          }
        }
        // Admin sees all

        const testSeries = await db.collection('testSeries').find(query).toArray();
        
        // Add creator names and enhanced metadata
        for (const test of testSeries) {
          const creator = await db.collection('users').findOne(
            { userId: test.createdBy },
            { projection: { name: 1, photo: 1, rating: 1, experience: 1 } }
          );
          test.createdByName = creator?.name || 'Unknown';
          test.createdByPhoto = creator?.photo || null;
          test.createdByRating = creator?.rating || 0;
          test.createdByExperience = creator?.experience || '';
          
          // Add attempt statistics for Udemy-style display
          const attemptStats = await db.collection('testAttempts').aggregate([
            { $match: { testSeriesId: test.testSeriesId, status: 'completed' } },
            { 
              $group: { 
                _id: null, 
                totalAttempts: { $sum: 1 },
                averageScore: { $avg: '$score' },
                averagePercentage: { $avg: { $multiply: [{ $divide: ['$score', '$totalQuestions'] }, 100] } }
              } 
            }
          ]).toArray();
          
          test.totalAttempts = attemptStats[0]?.totalAttempts || 0;
          test.averageScore = attemptStats[0]?.averageScore || 0;
          test.averagePercentage = attemptStats[0]?.averagePercentage || 0;
        }

        return NextResponse.json(testSeries, { headers: corsHeaders });
      }

      if (method === 'POST') {
        if (!user || !hasPermission(user.role, ['teacher', 'admin'])) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
        }

        const { title, description, category, duration, questions } = await request.json();

        const testSeriesId = uuidv4();
        const testSeries = {
          testSeriesId,
          title,
          description,
          category,
          duration: parseInt(duration),
          questions: questions || [],
          status: 'published', // New test series are published by default so teachers can see them immediately
          createdBy: user.userId,
          createdAt: new Date(),
          updatedAt: new Date()
        };

        await db.collection('testSeries').insertOne(testSeries);
        return NextResponse.json(testSeries, { headers: corsHeaders });
      }

      if (method === 'PUT' && path[1]) {
        if (!user || !hasPermission(user.role, ['teacher', 'admin'])) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
        }

        const testSeriesId = path[1];
        const updates = await request.json();
        updates.updatedAt = new Date();

        let query = { testSeriesId };
        if (user.role === 'teacher') {
          query.createdBy = user.userId;
        }

        const result = await db.collection('testSeries').updateOne(query, { $set: updates });
        
        if (result.matchedCount === 0) {
          return NextResponse.json({ error: 'Test series not found or unauthorized' }, { status: 404, headers: corsHeaders });
        }

        return NextResponse.json({ message: 'Test series updated successfully' }, { headers: corsHeaders });
      }

      if (method === 'DELETE' && path[1]) {
        if (!user || !hasPermission(user.role, ['teacher', 'admin'])) {
          return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
        }

        const testSeriesId = path[1];
        let query = { testSeriesId };
        if (user.role === 'teacher') {
          query.createdBy = user.userId;
        }

        const result = await db.collection('testSeries').deleteOne(query);
        
        if (result.deletedCount === 0) {
          return NextResponse.json({ error: 'Test series not found or unauthorized' }, { status: 404, headers: corsHeaders });
        }

        return NextResponse.json({ message: 'Test series deleted successfully' }, { headers: corsHeaders });
      }
    }

    // Test Attempts routes
    if (path[0] === 'test-attempts') {
      const user = getUserFromRequest(request);
      if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: corsHeaders });
      }

      if (method === 'GET') {
        let query = {};
        if (user.role === 'student') {
          query.studentId = user.userId;
        } else if (user.role === 'teacher') {
          // Get attempts for teacher's test series
          const teacherTests = await db.collection('testSeries').find({ createdBy: user.userId }).toArray();
          const testIds = teacherTests.map(test => test.testSeriesId);
          query.testSeriesId = { $in: testIds };
        }
        // Admin sees all

        const attempts = await db.collection('testAttempts').find(query).toArray();
        
        // Add test series names and student details
        for (const attempt of attempts) {
          const testSeries = await db.collection('testSeries').findOne({ testSeriesId: attempt.testSeriesId });
          attempt.testSeriesTitle = testSeries?.title || 'Unknown';
          
          if (user.role !== 'student') {
            const projection = user.role === 'teacher' 
              ? { name: 1 } // Teachers only see student names
              : { name: 1, email: 1, phone: 1 }; // Admins see full details
            
            const student = await db.collection('users').findOne(
              { userId: attempt.studentId },
              { projection }
            );
            attempt.studentDetails = student;
          }
        }

        return NextResponse.json(attempts, { headers: corsHeaders });
      }

      if (method === 'POST' && user.role === 'student') {
        // Start a new test attempt
        const { testSeriesId } = await request.json();
        
        // Check if already attempted
        const existingAttempt = await db.collection('testAttempts').findOne({
          testSeriesId,
          studentId: user.userId,
          status: 'completed'
        });
        
        if (existingAttempt) {
          return NextResponse.json({ error: 'Test already completed' }, { status: 400, headers: corsHeaders });
        }

        // Check for in-progress attempt
        const inProgressAttempt = await db.collection('testAttempts').findOne({
          testSeriesId,
          studentId: user.userId,
          status: 'in_progress'
        });

        if (inProgressAttempt) {
          return NextResponse.json({ 
            attemptId: inProgressAttempt.attemptId, 
            endTime: inProgressAttempt.endTime,
            totalQuestions: inProgressAttempt.totalQuestions,
            existing: true
          }, { headers: corsHeaders });
        }
        
        const testSeries = await db.collection('testSeries').findOne({ testSeriesId });
        if (!testSeries) {
          return NextResponse.json({ error: 'Test series not found' }, { status: 404, headers: corsHeaders });
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
        const requestBody = await request.json();
        const { questionId, answer, action } = requestBody;
        
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
            totalQuestions: testSeries.questions.length,
            timeExpired: true
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
          
          // Get the latest answers from the attempt
          const currentAttempt = await db.collection('testAttempts').findOne({ attemptId });
          
          // Create detailed results with solutions
          const detailedResults = [];
          for (const question of testSeries.questions) {
            const studentAnswer = currentAttempt.answers[question.questionId];
            const isCorrect = studentAnswer === question.correctAnswer;
            if (isCorrect) {
              score++;
            }
            
            detailedResults.push({
              questionId: question.questionId,
              question: question.question,
              options: question.options,
              studentAnswer: studentAnswer,
              correctAnswer: question.correctAnswer,
              isCorrect: isCorrect,
              explanation: question.explanation || 'No explanation provided'
            });
          }
          
          await db.collection('testAttempts').updateOne(
            { attemptId },
            { 
              $set: { 
                status: 'completed', 
                score,
                detailedResults,
                completedAt: new Date()
              } 
            }
          );
          
          return NextResponse.json({ 
            score,
            totalQuestions: testSeries.questions.length,
            percentage: Math.round((score / testSeries.questions.length) * 100),
            detailedResults,
            message: 'Test completed successfully'
          }, { headers: corsHeaders });
        }
      }
    }

    // Users management routes (Admin only)
    if (path[0] === 'users') {
      const user = getUserFromRequest(request);
      if (!user || !hasPermission(user.role, ['admin'])) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
      }

      if (method === 'GET') {
        const users = await db.collection('users').find(
          {},
          { projection: { password: 0, resetToken: 0, resetTokenExpiry: 0 } }
        ).toArray();
        return NextResponse.json(users, { headers: corsHeaders });
      }

      if (method === 'POST') {
        // Create new admin user
        const { username, password, name, email, role } = await request.json();

        const existingUser = await db.collection('users').findOne({ 
          $or: [{ username }, { email }] 
        });
        if (existingUser) {
          return NextResponse.json({ error: 'User already exists' }, { status: 400, headers: corsHeaders });
        }

        const userId = uuidv4();
        const hashedPassword = await bcrypt.hash(password, 12);

        const newUser = {
          userId,
          username,
          password: hashedPassword,
          name,
          email: email || null,
          role: role || 'admin',
          createdAt: new Date()
        };

        await db.collection('users').insertOne(newUser);
        
        const { password: _, ...userWithoutPassword } = newUser;
        return NextResponse.json(userWithoutPassword, { headers: corsHeaders });
      }
    }

    // Analytics routes
    if (path[0] === 'analytics') {
      const user = getUserFromRequest(request);
      if (!user || !hasPermission(user.role, ['teacher', 'admin'])) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 403, headers: corsHeaders });
      }

      if (method === 'GET') {
        let analytics = {};

        if (user.role === 'admin') {
          // System-wide analytics for admin
          const totalUsers = await db.collection('users').countDocuments();
          const totalTestSeries = await db.collection('testSeries').countDocuments();
          const totalAttempts = await db.collection('testAttempts').countDocuments();
          
          analytics = {
            totalUsers,
            totalTestSeries,
            totalAttempts,
            usersByRole: await db.collection('users').aggregate([
              { $group: { _id: '$role', count: { $sum: 1 } } }
            ]).toArray(),
            attemptsByStatus: await db.collection('testAttempts').aggregate([
              { $group: { _id: '$status', count: { $sum: 1 } } }
            ]).toArray()
          };
        } else if (user.role === 'teacher') {
          // Teacher-specific analytics
          const teacherTests = await db.collection('testSeries').find({ createdBy: user.userId });
          const testIds = (await teacherTests.toArray()).map(test => test.testSeriesId);
          
          const totalTestSeries = testIds.length;
          const totalAttempts = await db.collection('testAttempts').countDocuments({
            testSeriesId: { $in: testIds }
          });
          
          analytics = {
            totalTestSeries,
            totalAttempts,
            averageScore: await db.collection('testAttempts').aggregate([
              { $match: { testSeriesId: { $in: testIds }, status: 'completed' } },
              { $group: { _id: null, avgScore: { $avg: '$score' } } }
            ]).toArray()
          };
        }

        return NextResponse.json(analytics, { headers: corsHeaders });
      }
    }

    return NextResponse.json({ error: 'Route not found' }, { status: 404, headers: corsHeaders });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500, headers: corsHeaders });
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as OPTIONS };