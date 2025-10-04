const axios = require('axios');

const API_BASE = 'https://teacher-test-upload.preview.emergentagent.com/api';

async function testStudentFlow() {
  try {
    console.log('🧪 Testing Student Flow...\n');

    // 1. Test Categories API
    console.log('1. Testing Categories API...');
    const categoriesResponse = await axios.get(`${API_BASE}/categories`);
    console.log('✅ Categories loaded:', categoriesResponse.data.length);
    console.log('   Available categories:', categoriesResponse.data.map(c => c.name).join(', '));

    // 2. Test Teachers API  
    console.log('\n2. Testing Teachers API...');
    const teachersResponse = await axios.get(`${API_BASE}/teachers`);
    console.log('✅ Teachers loaded:', teachersResponse.data.length);
    console.log('   Available teachers:', teachersResponse.data.map(t => t.name).join(', '));

    // 3. Test Teachers by Category (should still return all teachers now)
    console.log('\n3. Testing Teachers by Category...');
    const categoryId = categoriesResponse.data[0].categoryId;
    const teachersByCategoryResponse = await axios.get(`${API_BASE}/teachers?category=${categoryId}`);
    console.log('✅ Teachers by category loaded:', teachersByCategoryResponse.data.length);

    // 4. Register a test student
    console.log('\n4. Registering Test Student...');
    const studentData = {
      username: `teststudent_${Date.now()}`,
      password: 'student123',
      name: 'Test Student',
      email: `teststudent${Date.now()}@example.com`,
      role: 'student'
    };

    const registerResponse = await axios.post(`${API_BASE}/auth/register`, studentData);
    console.log('✅ Student registered successfully');
    
    const studentToken = registerResponse.data.token;

    // 5. Update student preferences
    console.log('\n5. Updating Student Preferences...');
    const selectedCategory = categoriesResponse.data[0].categoryId;
    const selectedTeacher = teachersResponse.data[0].userId;
    
    await axios.put(`${API_BASE}/auth/profile`, {
      selectedCategory,
      selectedTeacher
    }, {
      headers: { Authorization: `Bearer ${studentToken}` }
    });
    console.log('✅ Student preferences updated');
    console.log(`   Selected Category: ${categoriesResponse.data[0].name}`);
    console.log(`   Selected Teacher: ${teachersResponse.data[0].name}`);

    // 6. Test student can see test series
    console.log('\n6. Testing Student Test Series Access...');
    const testSeriesResponse = await axios.get(`${API_BASE}/test-series`, {
      headers: { Authorization: `Bearer ${studentToken}` }
    });
    console.log('✅ Test series loaded for student:', testSeriesResponse.data.length);
    
    if (testSeriesResponse.data.length > 0) {
      console.log('   Available tests:');
      testSeriesResponse.data.forEach(test => {
        console.log(`   - ${test.title} (${test.category})`);
      });
    } else {
      console.log('   No test series found for this student');
    }

    console.log('\n🎉 All tests passed! Student flow is working correctly.');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data?.error || error.message);
  }
}

testStudentFlow();