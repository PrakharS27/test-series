'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Progress } from '@/components/ui/progress';
import { BookOpen, Users, BarChart3, Plus, Edit, Trash2, Play, Clock, CheckCircle, X, ChevronLeft, ChevronRight, Upload, FileText, User, Building, Phone, GraduationCap, Camera, Download, Mail, Lock } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = '/api';

export default function TestSeriesApp() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [testSeries, setTestSeries] = useState([]);
  const [attempts, setAttempts] = useState([]);
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [categories, setCategories] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [currentTest, setCurrentTest] = useState(null);
  const [currentAttempt, setCurrentAttempt] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [testCompleted, setTestCompleted] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [profile, setProfile] = useState(null);
  
  // New state for enhanced features
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTeacher, setSelectedTeacher] = useState('');
  const [authStep, setAuthStep] = useState('login'); // login, register, forgot-password
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [activeCategory, setActiveCategory] = useState('all'); // for category navigation
  const [showTeachersList, setShowTeachersList] = useState(false);
  const [categoryTeachers, setCategoryTeachers] = useState([]);
  const [showDetailedResults, setShowDetailedResults] = useState(false);
  const [detailedResults, setDetailedResults] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [previewTest, setPreviewTest] = useState(null);

  // Authentication functions
  const login = async (credentials) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.token);
        setUser(data.user);
        setIsAuthenticated(true);
        setAuthStep('dashboard');
        toast.success('Login successful!');
      } else {
        toast.error(data.error || 'Login failed');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.token);
        setUser(data.user);
        setIsAuthenticated(true);
        setAuthStep('dashboard');
        toast.success('Registration successful!');
      } else {
        toast.error(data.error || 'Registration failed');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setAuthStep('login');
    toast.success('Logged out successfully');
  };

  // Load categories
  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  // Load teachers by category
  const loadTeachersByCategory = async (category) => {
    try {
      const response = await fetch(`${API_BASE}/categories?withTeachers=true`);
      const categoriesData = await response.json();
      const categoryData = categoriesData.find(cat => cat.name === category);
      setCategoryTeachers(categoryData?.teachers || []);
      setShowTeachersList(true);
    } catch (error) {
      console.error('Error loading teachers by category:', error);
    }
  };

  // Preview test for teachers
  const previewTestSeries = async (testSeriesId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-series?preview=true`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const tests = await response.json();
      const test = tests.find(t => t.testSeriesId === testSeriesId);
      setPreviewTest(test);
      setShowPreview(true);
    } catch (error) {
      console.error('Error loading preview:', error);
      toast.error('Failed to load preview');
    }
  };

  // Update student preferences
  const updateStudentPreferences = async (category, teacher) => {
    try {
      const response = await fetch(`${API_BASE}/auth/profile`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          selectedCategory: category, 
          selectedTeacher: teacher 
        })
      });
      
      if (response.ok) {
        setUser(prev => ({ 
          ...prev, 
          selectedCategory: category, 
          selectedTeacher: teacher 
        }));
        setAuthStep('dashboard');
        toast.success('Preferences updated successfully!');
      }
    } catch (error) {
      toast.error('Failed to update preferences');
    }
  };

  // Load data functions
  const loadTestSeries = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-series`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setTestSeries(data);
    } catch (error) {
      console.error('Error loading test series:', error);
    }
  };

  const loadAttempts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-attempts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setAttempts(data);
    } catch (error) {
      console.error('Error loading attempts:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const loadProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/auth/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  // Test management functions
  const createTestSeries = async (testData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-series`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(testData)
      });
      
      if (response.ok) {
        toast.success('Test series created successfully!');
        loadTestSeries();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to create test series');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  const deleteTestSeries = async (testSeriesId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-series/${testSeriesId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        toast.success('Test series deleted successfully!');
        loadTestSeries();
      } else {
        toast.error('Failed to delete test series');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  // Test taking functions
  const startTest = async (testSeriesId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-attempts`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ testSeriesId })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setCurrentAttempt(data);
        
        // Load test details
        const testResponse = await fetch(`${API_BASE}/test-series`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const tests = await testResponse.json();
        const test = tests.find(t => t.testSeriesId === testSeriesId);
        setCurrentTest(test);
        
        // Set up timer
        const endTime = new Date(data.endTime);
        const now = new Date();
        const timeLeftMs = endTime.getTime() - now.getTime();
        setTimeLeft(Math.max(0, Math.floor(timeLeftMs / 1000)));
        
        toast.success(data.existing ? 'Resuming test...' : 'Test started!');
      } else {
        toast.error(data.error || 'Failed to start test');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  const submitAnswer = async (questionId, answer) => {
    if (!currentAttempt) return;
    
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_BASE}/test-attempts/${currentAttempt.attemptId}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ 
          action: 'submit_answer',
          questionId, 
          answer 
        })
      });
      
      setAnswers(prev => ({ ...prev, [questionId]: answer }));
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const completeTest = async () => {
    if (!currentAttempt) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/test-attempts/${currentAttempt.attemptId}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ action: 'complete_test' })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setTestResult(data);
        setDetailedResults(data.detailedResults);
        setTestCompleted(true);
        setShowSubmitDialog(false); // Close dialog immediately
        toast.success('Test submitted successfully!');
      } else {
        toast.error(data.error || 'Failed to submit test');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  // File upload functions
  const uploadPhoto = async (file) => {
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('photo', file);
      
      const response = await fetch(`${API_BASE}/upload/photo`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success('Photo uploaded successfully!');
        loadProfile();
      } else {
        toast.error(data.error || 'Failed to upload photo');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  const uploadCSV = async (file, testSeriesId) => {
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('csv', file);
      formData.append('testSeriesId', testSeriesId);
      
      const response = await fetch(`${API_BASE}/upload/csv`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success(data.message);
        loadTestSeries();
      } else {
        toast.error(data.error || 'Failed to upload CSV');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  // Password reset functions
  const forgotPassword = async (email) => {
    try {
      const response = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success('Password reset link sent to your email!');
        return data.resetToken; // For testing - remove in production
      } else {
        toast.error(data.error || 'Failed to send reset link');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  const resetPassword = async (resetToken, newPassword) => {
    try {
      const response = await fetch(`${API_BASE}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resetToken, newPassword })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success('Password reset successfully!');
        setAuthStep('login');
      } else {
        toast.error(data.error || 'Failed to reset password');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  // Category management
  const createCategory = async (categoryData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/categories`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(categoryData)
      });
      
      if (response.ok) {
        toast.success('Category created successfully!');
        loadCategories();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to create category');
      }
    } catch (error) {
      toast.error('Network error. Please try again.');
    }
  };

  // Timer effect
  useEffect(() => {
    if (timeLeft > 0 && currentTest) {
      const timer = setTimeout(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && currentTest && !testCompleted) {
      // Auto submit when time expires
      completeTest();
    }
  }, [timeLeft, currentTest, testCompleted]);

  // Initial load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      const decoded = JSON.parse(atob(token.split('.')[1]));
      setUser(decoded);
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  // Load data when authenticated
  useEffect(() => {
    if (isAuthenticated && authStep === 'login') {
      loadCategories();
      loadTestSeries();
      loadAttempts();
      loadProfile();
      if (user?.role === 'teacher' || user?.role === 'admin') {
        loadAnalytics();
      }
      if (user?.role === 'admin') {
        loadUsers();
      }
    }
  }, [isAuthenticated, user?.role, authStep]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Authentication UI (Simplified - no category/teacher selection for students)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">
              {authStep === 'login' && 'Test Series Platform'}
              {authStep === 'register' && 'Create Account'}
              {authStep === 'forgot-password' && 'Reset Password'}
            </CardTitle>
            <CardDescription>
              {(authStep === 'login' || authStep === 'register') && 'Access your personalized learning dashboard'}
              {authStep === 'forgot-password' && 'Enter your email to reset password'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Login Form */}
            {authStep === 'login' && <LoginForm />}

            {/* Register Form */}
            {authStep === 'register' && <RegisterForm />}

            {/* Forgot Password Form */}
            {authStep === 'forgot-password' && <ForgotPasswordForm />}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Test Taking Interface
  if (currentTest && !testCompleted) {
    const question = currentTest.questions[currentQuestion];
    const hours = Math.floor(timeLeft / 3600);
    const minutes = Math.floor((timeLeft % 3600) / 60);
    const seconds = timeLeft % 60;

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold">{currentTest.title}</h1>
              <p className="text-sm text-gray-600">
                Question {currentQuestion + 1} of {currentTest.questions.length}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-orange-500" />
                <span className="font-mono text-lg">
                  {String(hours).padStart(2, '0')}:{String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                </span>
              </div>
              <Button 
                onClick={() => setShowSubmitDialog(true)}
                variant="destructive"
              >
                Submit Test
              </Button>
            </div>
          </div>
        </div>

        <div className="max-w-4xl mx-auto p-6">
          <Card>
            <CardHeader>
              <CardTitle>Question {currentQuestion + 1}</CardTitle>
              <CardDescription>{question?.question}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <RadioGroup 
                value={answers[question?.questionId]?.toString() || ''} 
                onValueChange={(value) => {
                  const answerIndex = parseInt(value);
                  setAnswers(prev => ({ ...prev, [question?.questionId]: answerIndex }));
                  submitAnswer(question?.questionId, answerIndex);
                }}
              >
                {question?.options.map((option, index) => (
                  <div key={`${question?.questionId}-${index}`} className="flex items-center space-x-2">
                    <RadioGroupItem 
                      value={index.toString()} 
                      id={`question-${question?.questionId}-option-${index}`} 
                    />
                    <Label 
                      htmlFor={`question-${question?.questionId}-option-${index}`} 
                      className="text-sm cursor-pointer"
                    >
                      {option}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
              
              <div className="flex justify-between pt-6">
                <Button 
                  variant="outline" 
                  onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                  disabled={currentQuestion === 0}
                >
                  <ChevronLeft className="mr-2 h-4 w-4" /> Previous
                </Button>
                <Button 
                  onClick={() => setCurrentQuestion(Math.min(currentTest.questions.length - 1, currentQuestion + 1))}
                  disabled={currentQuestion === currentTest.questions.length - 1}
                >
                  Next <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Fixed Submit Dialog */}
        <AlertDialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Submit Test</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to submit your test? You won't be able to make any changes after submission.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={completeTest}>
                Submit Test
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    );
  }

  // Test Results
  if (testCompleted && testResult) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Test Completed!</CardTitle>
            <CardDescription>Here are your results</CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-6">
            <div>
              <div className="text-4xl font-bold text-blue-600">{testResult.score}</div>
              <div className="text-lg text-gray-600">out of {testResult.totalQuestions}</div>
              <div className="text-2xl font-semibold text-green-600">{testResult.percentage}%</div>
            </div>
            <Button 
              onClick={() => {
                setCurrentTest(null);
                setCurrentAttempt(null);
                setTestCompleted(false);
                setTestResult(null);
                setAnswers({});
                setCurrentQuestion(0);
                loadTestSeries();
                loadAttempts();
              }}
              className="w-full"
            >
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Main Dashboard
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Test Series Platform</h1>
            <p className="text-sm text-gray-600">
              Welcome back, {user?.username} 
              <Badge variant="secondary" className="ml-2">
                {user?.role?.toUpperCase()}
              </Badge>
            </p>
          </div>
          <Button variant="outline" onClick={logout}>
            Logout
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full" style={{
            gridTemplateColumns: user?.role === 'student' 
              ? '1fr 1fr 1fr' 
              : user?.role === 'teacher'
              ? '1fr 1fr 1fr 1fr 1fr'
              : '1fr 1fr 1fr 1fr 1fr 1fr 1fr'
          }}>
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="tests">Test Series</TabsTrigger>
            <TabsTrigger value="profile">Profile</TabsTrigger>
            {(user?.role === 'teacher' || user?.role === 'admin') && (
              <TabsTrigger value="results">Results</TabsTrigger>
            )}
            {(user?.role === 'teacher' || user?.role === 'admin') && (
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            )}
            {user?.role === 'admin' && (
              <TabsTrigger value="categories">Categories</TabsTrigger>
            )}
            {user?.role === 'admin' && (
              <TabsTrigger value="users">Users</TabsTrigger>
            )}
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="mt-6">
            <DashboardContent />
          </TabsContent>

          {/* Test Series Tab */}
          <TabsContent value="tests" className="mt-6">
            <TestSeriesContent />
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile" className="mt-6">
            <ProfileContent />
          </TabsContent>

          {/* Results Tab */}
          {(user?.role === 'teacher' || user?.role === 'admin') && (
            <TabsContent value="results" className="mt-6">
              <ResultsContent />
            </TabsContent>
          )}

          {/* Analytics Tab */}
          {(user?.role === 'teacher' || user?.role === 'admin') && (
            <TabsContent value="analytics" className="mt-6">
              <AnalyticsContent />
            </TabsContent>
          )}

          {/* Categories Tab */}
          {user?.role === 'admin' && (
            <TabsContent value="categories" className="mt-6">
              <CategoriesContent />
            </TabsContent>
          )}

          {/* Users Tab */}
          {user?.role === 'admin' && (
            <TabsContent value="users" className="mt-6">
              <UsersContent />
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );

  // Component Functions
  function LoginForm() {
    const [credentials, setCredentials] = useState({ username: '', password: '' });

    return (
      <form onSubmit={(e) => {
        e.preventDefault();
        login(credentials);
      }} className="space-y-4">
        <div>
          <Label htmlFor="username">Username</Label>
          <Input 
            id="username"
            value={credentials.username}
            onChange={(e) => setCredentials({...credentials, username: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input 
            id="password"
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            required
          />
        </div>
        <Button type="submit" className="w-full">Login</Button>
        <div className="text-center space-y-2">
          <Button 
            type="button" 
            variant="link" 
            onClick={() => setAuthStep('forgot-password')}
            className="text-sm"
          >
            Forgot Password?
          </Button>
          <div>
            <Button 
              type="button" 
              variant="link" 
              onClick={() => setAuthStep('register')}
            >
              Need an account? Register
            </Button>
          </div>
        </div>
      </form>
    );
  }

  function RegisterForm() {
    const [formData, setFormData] = useState({
      username: '', password: '', name: '', email: '', phone: '', role: 'student'
    });

    return (
      <form onSubmit={(e) => {
        e.preventDefault();
        register(formData);
      }} className="space-y-4">
        <div>
          <Label htmlFor="name">Full Name</Label>
          <Input 
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="username">Username</Label>
          <Input 
            id="username"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="email">Email</Label>
          <Input 
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="phone">Phone</Label>
          <Input 
            id="phone"
            value={formData.phone}
            onChange={(e) => setFormData({...formData, phone: e.target.value})}
          />
        </div>
        <div>
          <Label htmlFor="role">Role</Label>
          <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="student">Student</SelectItem>
              <SelectItem value="teacher">Teacher</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input 
            id="password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
        </div>
        <Button type="submit" className="w-full">Register</Button>
        <div className="text-center">
          <Button 
            type="button" 
            variant="link" 
            onClick={() => setAuthStep('login')}
          >
            Already have an account? Login
          </Button>
        </div>
      </form>
    );
  }

  function ForgotPasswordForm() {
    const [email, setEmail] = useState('');
    const [resetToken, setResetToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [step, setStep] = useState('email'); // email or reset

    return (
      <div className="space-y-4">
        {step === 'email' && (
          <form onSubmit={(e) => {
            e.preventDefault();
            forgotPassword(email).then(token => {
              if (token) {
                setResetToken(token);
                setStep('reset');
              }
            });
          }}>
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input 
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full mt-4">Send Reset Link</Button>
          </form>
        )}

        {step === 'reset' && (
          <form onSubmit={(e) => {
            e.preventDefault();
            resetPassword(resetToken, newPassword);
          }}>
            <div className="space-y-4">
              <div>
                <Label htmlFor="resetToken">Reset Token</Label>
                <Input 
                  id="resetToken"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="newPassword">New Password</Label>
                <Input 
                  id="newPassword"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </div>
            </div>
            <Button type="submit" className="w-full mt-4">Reset Password</Button>
          </form>
        )}

        <div className="text-center">
          <Button 
            type="button" 
            variant="link" 
            onClick={() => setAuthStep('login')}
          >
            Back to Login
          </Button>
        </div>
      </div>
    );
  }

  function DashboardContent() {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {user?.role === 'student' && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Available Tests</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{testSeries.length}</div>
                <p className="text-xs text-muted-foreground">
                  Test series available to take
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tests Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{attempts.filter(a => a.status === 'completed').length}</div>
                <p className="text-xs text-muted-foreground">
                  Tests you have completed
                </p>
              </CardContent>
            </Card>
            {user.selectedCategory && user.selectedTeacher && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Your Selection</CardTitle>
                  <GraduationCap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-sm">
                    <div>Category: <span className="font-medium">{categories.find(c => c.categoryId === user.selectedCategory)?.name || 'Selected'}</span></div>
                    <div>Teacher: <span className="font-medium">{teachers.find(t => t.userId === user.selectedTeacher)?.name || 'Selected'}</span></div>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
        
        {(user?.role === 'teacher' || user?.role === 'admin') && analytics && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Test Series</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics.totalTestSeries}</div>
                <p className="text-xs text-muted-foreground">
                  {user?.role === 'teacher' ? 'Your test series' : 'Total test series'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Attempts</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics.totalAttempts}</div>
                <p className="text-xs text-muted-foreground">
                  Test attempts made
                </p>
              </CardContent>
            </Card>
            {user?.role === 'admin' && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.totalUsers || users.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Registered users
                  </p>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    );
  }

  function TestSeriesContent() {
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [showCSVDialog, setShowCSVDialog] = useState(false);
    const [selectedTestForCSV, setSelectedTestForCSV] = useState('');

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Test Series</h2>
          {(user?.role === 'teacher' || user?.role === 'admin') && (
            <div className="flex space-x-2">
              <Button onClick={() => setShowCSVDialog(true)}>
                <Upload className="mr-2 h-4 w-4" /> Upload CSV
              </Button>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="mr-2 h-4 w-4" /> Create Test
              </Button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testSeries.map((test) => (
            <Card key={test.testSeriesId} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{test.title}</CardTitle>
                    <CardDescription className="mt-1">{test.description}</CardDescription>
                  </div>
                  {(user?.role === 'teacher' || user?.role === 'admin') && test.createdBy === user?.userId && (
                    <div className="flex space-x-1">
                      <Button size="sm" variant="ghost" onClick={() => deleteTestSeries(test.testSeriesId)}>
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center justify-between">
                    <span>Category:</span>
                    <Badge variant="outline">{test.category}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Duration:</span>
                    <span>{test.duration} minutes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Questions:</span>
                    <span>{test.questions.length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Created by:</span>
                    <span>{test.createdByName}</span>
                  </div>
                </div>
                {user?.role === 'student' && (
                  <Button 
                    className="w-full mt-4" 
                    onClick={() => startTest(test.testSeriesId)}
                    disabled={attempts.some(a => a.testSeriesId === test.testSeriesId && a.status === 'completed')}
                  >
                    {attempts.some(a => a.testSeriesId === test.testSeriesId && a.status === 'completed') ? (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Completed
                      </>
                    ) : attempts.some(a => a.testSeriesId === test.testSeriesId && a.status === 'in_progress') ? (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Resume Test
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Start Test
                      </>
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Create Test Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create Test Series</DialogTitle>
              <DialogDescription>Create a new test series for your students</DialogDescription>
            </DialogHeader>
            <CreateTestForm onSuccess={() => setShowCreateDialog(false)} />
          </DialogContent>
        </Dialog>

        {/* CSV Upload Dialog */}
        <Dialog open={showCSVDialog} onOpenChange={setShowCSVDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Upload Questions via CSV</DialogTitle>
              <DialogDescription>Upload questions in CSV format: Question, Option A, Option B, Option C, Option D, Correct Answer, Explanation</DialogDescription>
            </DialogHeader>
            <CSVUploadForm 
              testSeries={testSeries.filter(t => t.createdBy === user?.userId)}
              onSuccess={() => setShowCSVDialog(false)} 
            />
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  function CreateTestForm({ onSuccess }) {
    const [formData, setFormData] = useState({
      title: '', description: '', category: '', duration: 60
    });

    return (
      <form onSubmit={(e) => {
        e.preventDefault();
        createTestSeries(formData).then(() => {
          setFormData({ title: '', description: '', category: '', duration: 60 });
          onSuccess();
        });
      }} className="space-y-4">
        <div>
          <Label htmlFor="title">Title</Label>
          <Input 
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea 
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows={3}
          />
        </div>
        <div>
          <Label htmlFor="category">Category</Label>
          <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map(category => (
                <SelectItem key={category.categoryId} value={category.name}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="duration">Duration (minutes)</Label>
          <Input 
            id="duration"
            type="number"
            value={formData.duration}
            onChange={(e) => setFormData({...formData, duration: parseInt(e.target.value)})}
            min="1"
            required
          />
        </div>
        <Button type="submit" className="w-full">Create Test Series</Button>
      </form>
    );
  }

  function CSVUploadForm({ testSeries, onSuccess }) {
    const [selectedTest, setSelectedTest] = useState('');
    const [file, setFile] = useState(null);

    return (
      <form onSubmit={(e) => {
        e.preventDefault();
        if (file && selectedTest) {
          uploadCSV(file, selectedTest).then(() => {
            setFile(null);
            setSelectedTest('');
            onSuccess();
          });
        }
      }} className="space-y-4">
        <div>
          <Label htmlFor="testSeries">Select Test Series</Label>
          <Select value={selectedTest} onValueChange={setSelectedTest}>
            <SelectTrigger>
              <SelectValue placeholder="Choose test series" />
            </SelectTrigger>
            <SelectContent>
              {testSeries.map(test => (
                <SelectItem key={test.testSeriesId} value={test.testSeriesId}>
                  {test.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="csvFile">CSV File</Label>
          <Input 
            id="csvFile"
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={!file || !selectedTest}>
          Upload Questions
        </Button>
      </form>
    );
  }

  function ProfileContent() {
    const [photoFile, setPhotoFile] = useState(null);

    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
            <CardDescription>Manage your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Photo Upload */}
            {(user?.role === 'teacher' || user?.role === 'admin') && (
              <div className="flex items-center space-x-4">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                  {profile?.photo ? (
                    <img src={profile.photo} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    <Camera className="h-8 w-8 text-gray-400" />
                  )}
                </div>
                <div>
                  <Label htmlFor="photo">Profile Photo</Label>
                  <Input 
                    id="photo"
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) uploadPhoto(file);
                    }}
                    className="mt-2"
                  />
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Full Name</Label>
                <Input value={profile?.name || ''} disabled />
              </div>
              <div>
                <Label>Username</Label>
                <Input value={profile?.username || ''} disabled />
              </div>
              <div>
                <Label>Email</Label>
                <Input value={profile?.email || ''} disabled />
              </div>
              <div>
                <Label>Phone</Label>
                <Input value={profile?.phone || ''} disabled />
              </div>
              <div>
                <Label>Role</Label>
                <Input value={profile?.role || ''} disabled />
              </div>
              <div>
                <Label>Joined</Label>
                <Input value={profile?.createdAt ? new Date(profile.createdAt).toLocaleDateString() : ''} disabled />
              </div>
            </div>

            {user?.role === 'student' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Selected Category</Label>
                  <Input value={categories.find(c => c.categoryId === profile?.selectedCategory)?.name || 'Not selected'} disabled />
                </div>
                <div>
                  <Label>Selected Teacher</Label>
                  <Input value={teachers.find(t => t.userId === profile?.selectedTeacher)?.name || 'Not selected'} disabled />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  function ResultsContent() {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Test Results</h2>
        <div className="grid gap-4">
          {attempts.map((attempt) => (
            <Card key={attempt.attemptId}>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <Label>Test</Label>
                    <p className="font-medium">{attempt.testSeriesTitle}</p>
                  </div>
                  <div>
                    <Label>Student</Label>
                    <p className="font-medium">{attempt.studentName}</p>
                    {attempt.studentDetails && (
                      <div className="text-sm text-gray-600 mt-1">
                        <div>{attempt.studentDetails.email}</div>
                        <div>{attempt.studentDetails.phone}</div>
                      </div>
                    )}
                  </div>
                  <div>
                    <Label>Score</Label>
                    <p className="font-medium">{attempt.score}/{attempt.totalQuestions}</p>
                    <p className="text-sm text-gray-600">{Math.round((attempt.score / attempt.totalQuestions) * 100)}%</p>
                  </div>
                  <div>
                    <Label>Status</Label>
                    <Badge variant={attempt.status === 'completed' ? 'default' : 'secondary'}>
                      {attempt.status}
                    </Badge>
                    {attempt.completedAt && (
                      <p className="text-sm text-gray-600 mt-1">
                        {new Date(attempt.completedAt).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  function AnalyticsContent() {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Analytics</h2>
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Test Series</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{analytics.totalTestSeries}</div>
                <p className="text-sm text-gray-600">Total created</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Total Attempts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{analytics.totalAttempts}</div>
                <p className="text-sm text-gray-600">By all students</p>
              </CardContent>
            </Card>
            {analytics.averageScore && (
              <Card>
                <CardHeader>
                  <CardTitle>Average Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{analytics.averageScore[0]?.avgScore?.toFixed(1) || 0}</div>
                  <p className="text-sm text-gray-600">Out of total questions</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    );
  }

  function CategoriesContent() {
    const [showCreateDialog, setShowCreateDialog] = useState(false);

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Categories</h2>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="mr-2 h-4 w-4" /> Add Category
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <Card key={category.categoryId}>
              <CardHeader>
                <CardTitle>{category.name}</CardTitle>
                <CardDescription>{category.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Created: {new Date(category.createdAt).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create Category</DialogTitle>
              <DialogDescription>Add a new test category</DialogDescription>
            </DialogHeader>
            <CreateCategoryForm onSuccess={() => setShowCreateDialog(false)} />
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  function CreateCategoryForm({ onSuccess }) {
    const [formData, setFormData] = useState({ name: '', description: '' });

    return (
      <form onSubmit={(e) => {
        e.preventDefault();
        createCategory(formData).then(() => {
          setFormData({ name: '', description: '' });
          onSuccess();
        });
      }} className="space-y-4">
        <div>
          <Label htmlFor="name">Category Name</Label>
          <Input 
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea 
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows={3}
          />
        </div>
        <Button type="submit" className="w-full">Create Category</Button>
      </form>
    );
  }

  function UsersContent() {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Users</h2>
        <div className="grid gap-4">
          {users.map((user) => (
            <Card key={user.userId}>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                    {user.photo ? (
                      <img src={user.photo} alt={user.name} className="w-full h-full object-cover" />
                    ) : (
                      <User className="h-6 w-6 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <Label>Name</Label>
                      <p className="font-medium">{user.name}</p>
                      <p className="text-sm text-gray-600">@{user.username}</p>
                    </div>
                    <div>
                      <Label>Role</Label>
                      <Badge>{user.role.toUpperCase()}</Badge>
                    </div>
                    <div>
                      <Label>Email</Label>
                      <p className="text-sm">{user.email || 'Not provided'}</p>
                    </div>
                    <div>
                      <Label>Joined</Label>
                      <p className="text-sm">{new Date(user.createdAt).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }
}