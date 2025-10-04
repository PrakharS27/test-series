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
import { BookOpen, Users, BarChart3, Plus, Edit, Trash2, Play, Clock, CheckCircle, X, ChevronLeft, ChevronRight } from 'lucide-react';
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
  const [currentTest, setCurrentTest] = useState(null);
  const [currentAttempt, setCurrentAttempt] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [testCompleted, setTestCompleted] = useState(false);
  const [testResult, setTestResult] = useState(null);

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
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
        setIsAuthenticated(true);
        toast.success('Login successful!');
        return true;
      } else {
        toast.error(data.error || 'Login failed');
        return false;
      }
    } catch (error) {
      toast.error('Login failed');
      return false;
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
        toast.success('Registration successful! Please login.');
        return true;
      } else {
        toast.error(data.error || 'Registration failed');
        return false;
      }
    } catch (error) {
      toast.error('Registration failed');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    setCurrentTest(null);
    setCurrentAttempt(null);
    setTestCompleted(false);
    toast.success('Logged out successfully');
  };

  // API helper function
  const apiCall = async (endpoint, options = {}) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.headers
      }
    });
    
    if (response.status === 401) {
      logout();
      return null;
    }
    
    return response;
  };

  // Load initial data
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
      setIsAuthenticated(true);
    }
    
    setLoading(false);
  }, []);

  // Load data based on user role
  useEffect(() => {
    if (isAuthenticated && user) {
      loadTestSeries();
      loadAttempts();
      if (user.role === 'admin') {
        loadUsers();
      }
      if (user.role === 'teacher' || user.role === 'admin') {
        loadAnalytics();
      }
    }
  }, [isAuthenticated, user]);

  // Timer effect for test taking
  useEffect(() => {
    let timer;
    if (currentAttempt && timeLeft > 0 && !testCompleted) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            submitTest();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [currentAttempt, timeLeft, testCompleted]);

  const loadTestSeries = async () => {
    try {
      const response = await apiCall('/test-series');
      if (response?.ok) {
        const data = await response.json();
        setTestSeries(data);
      }
    } catch (error) {
      console.error('Error loading test series:', error);
    }
  };

  const loadAttempts = async () => {
    try {
      const response = await apiCall('/test-attempts');
      if (response?.ok) {
        const data = await response.json();
        setAttempts(data);
      }
    } catch (error) {
      console.error('Error loading attempts:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await apiCall('/users');
      if (response?.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await apiCall('/analytics');
      if (response?.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  // Test management functions
  const createTestSeries = async (testData) => {
    try {
      const response = await apiCall('/test-series', {
        method: 'POST',
        body: JSON.stringify(testData)
      });
      
      if (response?.ok) {
        toast.success('Test series created successfully!');
        loadTestSeries();
        return true;
      } else {
        const data = await response.json();
        toast.error(data.error || 'Failed to create test series');
        return false;
      }
    } catch (error) {
      toast.error('Failed to create test series');
      return false;
    }
  };

  const deleteTestSeries = async (testSeriesId) => {
    try {
      const response = await apiCall(`/test-series/${testSeriesId}`, {
        method: 'DELETE'
      });
      
      if (response?.ok) {
        toast.success('Test series deleted successfully!');
        loadTestSeries();
      } else {
        toast.error('Failed to delete test series');
      }
    } catch (error) {
      toast.error('Failed to delete test series');
    }
  };

  // Test taking functions
  const startTest = async (testSeriesId) => {
    try {
      const response = await apiCall('/test-attempts', {
        method: 'POST',
        body: JSON.stringify({ testSeriesId })
      });
      
      if (response?.ok) {
        const data = await response.json();
        
        // Load test series details
        const testResponse = await apiCall(`/test-series/${testSeriesId}`);
        if (testResponse?.ok) {
          const testData = await testResponse.json();
          setCurrentTest(testData);
          setCurrentAttempt({ 
            attemptId: data.attemptId, 
            testSeriesId,
            endTime: data.endTime 
          });
          setCurrentQuestion(0);
          setAnswers({});
          
          // Calculate time left
          const endTime = new Date(data.endTime);
          const now = new Date();
          const timeLeftSeconds = Math.max(0, Math.floor((endTime - now) / 1000));
          setTimeLeft(timeLeftSeconds);
          
          toast.success('Test started!');
        }
      } else {
        const data = await response.json();
        toast.error(data.error || 'Failed to start test');
      }
    } catch (error) {
      toast.error('Failed to start test');
    }
  };

  const saveAnswer = async (questionId, answer) => {
    if (!currentAttempt) return;
    
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
    
    try {
      await apiCall(`/test-attempts/${currentAttempt.attemptId}`, {
        method: 'PUT',
        body: JSON.stringify({ 
          questionId, 
          answer, 
          action: 'submit_answer' 
        })
      });
    } catch (error) {
      console.error('Error saving answer:', error);
    }
  };

  const submitTest = async () => {
    if (!currentAttempt) return;
    
    try {
      const response = await apiCall(`/test-attempts/${currentAttempt.attemptId}`, {
        method: 'PUT',
        body: JSON.stringify({ action: 'complete_test' })
      });
      
      if (response?.ok) {
        const data = await response.json();
        setTestResult(data);
        setTestCompleted(true);
        toast.success('Test completed successfully!');
      }
    } catch (error) {
      toast.error('Failed to submit test');
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // Login/Register Component
  const AuthComponent = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
      username: '',
      password: '',
      name: '',
      role: 'student'
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (isLogin) {
        await login({ username: formData.username, password: formData.password });
      } else {
        const success = await register(formData);
        if (success) {
          setIsLogin(true);
          setFormData({ username: '', password: '', name: '', role: 'student' });
        }
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold">
              {isLogin ? 'Login' : 'Register'} - Test Series App
            </CardTitle>
            <CardDescription>
              {isLogin ? 'Sign in to your account' : 'Create a new account'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>
              
              {!isLogin && (
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
              )}
              
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>
              
              {!isLogin && (
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="student">Student</SelectItem>
                      <SelectItem value="teacher">Teacher</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <Button type="submit" className="w-full">
                {isLogin ? 'Login' : 'Register'}
              </Button>
            </form>
            
            <div className="mt-4 text-center">
              <Button
                variant="link"
                onClick={() => setIsLogin(!isLogin)}
              >
                {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  // Test Taking Component
  const TestTakingComponent = () => {
    if (testCompleted && testResult) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-100 p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-bold text-green-600">
                <CheckCircle className="w-12 h-12 mx-auto mb-2" />
                Test Completed!
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-6">
              <div className="text-6xl font-bold text-blue-600">
                {testResult.score}/{testResult.totalQuestions}
              </div>
              <div className="text-2xl text-gray-600">
                Score: {testResult.percentage}%
              </div>
              <div className="flex justify-center space-x-4">
                <Button onClick={() => {
                  setCurrentTest(null);
                  setCurrentAttempt(null);
                  setTestCompleted(false);
                  setTestResult(null);
                  loadAttempts();
                }}>
                  Back to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    if (!currentTest || !currentAttempt) return null;

    const question = currentTest.questions[currentQuestion];
    const progress = ((currentQuestion + 1) / currentTest.questions.length) * 100;

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h1 className="text-2xl font-bold">{currentTest.title}</h1>
                <p className="text-gray-600">Question {currentQuestion + 1} of {currentTest.questions.length}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center space-x-2 text-lg font-semibold">
                  <Clock className="w-5 h-5" />
                  <span className={timeLeft < 300 ? 'text-red-600' : 'text-blue-600'}>
                    {formatTime(timeLeft)}
                  </span>
                </div>
              </div>
            </div>
            <Progress value={progress} className="w-full" />
          </div>

          {/* Question */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-xl">{question.question}</CardTitle>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={answers[question.questionId] || ''}
                onValueChange={(value) => saveAnswer(question.questionId, value)}
              >
                {question.options.map((option, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <RadioGroupItem value={option} id={`option-${index}`} />
                    <Label htmlFor={`option-${index}`} className="text-lg cursor-pointer flex-1 p-3 rounded hover:bg-gray-50">
                      {option}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            <div className="flex space-x-2">
              {currentQuestion === currentTest.questions.length - 1 ? (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button className="bg-green-600 hover:bg-green-700">
                      Submit Test
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Submit Test?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to submit the test? You cannot change your answers after submission.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={submitTest}>
                        Submit Test
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              ) : (
                <Button
                  onClick={() => setCurrentQuestion(Math.min(currentTest.questions.length - 1, currentQuestion + 1))}
                >
                  Next
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Create Test Series Dialog
  const CreateTestDialog = ({ onSuccess }) => {
    const [open, setOpen] = useState(false);
    const [formData, setFormData] = useState({
      title: '',
      description: '',
      category: '',
      duration: 60,
      questions: [{ question: '', options: ['', '', '', ''], correctAnswer: '' }]
    });

    const addQuestion = () => {
      setFormData({
        ...formData,
        questions: [...formData.questions, { question: '', options: ['', '', '', ''], correctAnswer: '' }]
      });
    };

    const updateQuestion = (index, field, value) => {
      const updatedQuestions = [...formData.questions];
      if (field === 'options') {
        updatedQuestions[index].options = value;
      } else {
        updatedQuestions[index][field] = value;
      }
      setFormData({ ...formData, questions: updatedQuestions });
    };

    const updateOption = (questionIndex, optionIndex, value) => {
      const updatedQuestions = [...formData.questions];
      updatedQuestions[questionIndex].options[optionIndex] = value;
      setFormData({ ...formData, questions: updatedQuestions });
    };

    const removeQuestion = (index) => {
      setFormData({
        ...formData,
        questions: formData.questions.filter((_, i) => i !== index)
      });
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      const success = await createTestSeries(formData);
      if (success) {
        setOpen(false);
        setFormData({
          title: '',
          description: '',
          category: '',
          duration: 60,
          questions: [{ question: '', options: ['', '', '', ''], correctAnswer: '' }]
        });
        onSuccess();
      }
    };

    return (
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Test Series
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Test Series</DialogTitle>
            <DialogDescription>
              Create a new test series with multiple choice questions
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="e.g., JEE Mains, CUET PG"
                  required
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="duration">Duration (minutes)</Label>
              <Input
                id="duration"
                type="number"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
                min="1"
                required
              />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-4">
                <Label className="text-lg font-semibold">Questions</Label>
                <Button type="button" onClick={addQuestion} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Question
                </Button>
              </div>
              
              {formData.questions.map((question, qIndex) => (
                <Card key={qIndex} className="p-4">
                  <div className="flex justify-between items-start mb-4">
                    <Label className="text-md font-medium">Question {qIndex + 1}</Label>
                    {formData.questions.length > 1 && (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => removeQuestion(qIndex)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                  
                  <div className="space-y-4">
                    <Textarea
                      placeholder="Enter question"
                      value={question.question}
                      onChange={(e) => updateQuestion(qIndex, 'question', e.target.value)}
                      required
                    />
                    
                    <div className="grid grid-cols-2 gap-2">
                      {question.options.map((option, oIndex) => (
                        <Input
                          key={oIndex}
                          placeholder={`Option ${String.fromCharCode(65 + oIndex)}`}
                          value={option}
                          onChange={(e) => updateOption(qIndex, oIndex, e.target.value)}
                          required
                        />
                      ))}
                    </div>
                    
                    <div>
                      <Label>Correct Answer</Label>
                      <Select
                        value={question.correctAnswer}
                        onValueChange={(value) => updateQuestion(qIndex, 'correctAnswer', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select correct answer" />
                        </SelectTrigger>
                        <SelectContent>
                          {question.options.map((option, oIndex) => (
                            option && (
                              <SelectItem key={oIndex} value={option}>
                                {String.fromCharCode(65 + oIndex)}: {option}
                              </SelectItem>
                            )
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                Create Test Series
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    );
  };

  // Main Dashboard
  const Dashboard = () => {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Test Series Platform</h1>
                <p className="text-gray-600">Welcome back, {user?.name}!</p>
              </div>
              <div className="flex items-center space-x-4">
                <Badge variant={user?.role === 'admin' ? 'destructive' : user?.role === 'teacher' ? 'secondary' : 'default'}>
                  {user?.role?.toUpperCase()}
                </Badge>
                <Button variant="outline" onClick={logout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Tabs defaultValue="dashboard" className="w-full">
            <TabsList className="grid w-full" style={{
              gridTemplateColumns: user?.role === 'student' 
                ? '1fr 1fr' 
                : user?.role === 'teacher'
                ? '1fr 1fr 1fr 1fr'
                : '1fr 1fr 1fr 1fr 1fr'
            }}>
              <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
              <TabsTrigger value="tests">Test Series</TabsTrigger>
              {(user?.role === 'teacher' || user?.role === 'admin') && (
                <TabsTrigger value="results">Results</TabsTrigger>
              )}
              {(user?.role === 'teacher' || user?.role === 'admin') && (
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              )}
              {user?.role === 'admin' && (
                <TabsTrigger value="users">Users</TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="dashboard" className="mt-6">
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
                    {user?.role === 'teacher' && (
                      <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                          <CardTitle className="text-sm font-medium">Average Score</CardTitle>
                          <BarChart3 className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">{analytics.averageScore?.toFixed(1) || '0'}</div>
                          <p className="text-xs text-muted-foreground">
                            Out of total questions
                          </p>
                        </CardContent>
                      </Card>
                    )}
                  </>
                )}
              </div>
            </TabsContent>

            <TabsContent value="tests" className="mt-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Test Series</h2>
                {(user?.role === 'teacher' || user?.role === 'admin') && (
                  <CreateTestDialog onSuccess={loadTestSeries} />
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {testSeries.map((test) => {
                  const hasAttempted = attempts.some(a => a.testSeriesId === test.testSeriesId && a.status === 'completed');
                  
                  return (
                    <Card key={test.testSeriesId} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <CardTitle className="flex justify-between items-start">
                          <span>{test.title}</span>
                          {(user?.role === 'teacher' || user?.role === 'admin') && test.createdBy === user?.userId && (
                            <div className="flex space-x-2">
                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button variant="destructive" size="sm">
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Delete Test Series?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Are you sure you want to delete this test series? This action cannot be undone.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction onClick={() => deleteTestSeries(test.testSeriesId)}>
                                      Delete
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          )}
                        </CardTitle>
                        <CardDescription>{test.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Category:</span>
                            <Badge variant="secondary">{test.category}</Badge>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Duration:</span>
                            <span>{test.duration} minutes</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Questions:</span>
                            <span>{test.questions?.length || 0}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Created by:</span>
                            <span>{test.createdByName}</span>
                          </div>
                          
                          {user?.role === 'student' && (
                            <div className="pt-4">
                              {hasAttempted ? (
                                <Badge variant="success">Completed</Badge>
                              ) : (
                                <Button
                                  onClick={() => startTest(test.testSeriesId)}
                                  className="w-full"
                                >
                                  <Play className="w-4 h-4 mr-2" />
                                  Start Test
                                </Button>
                              )}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {(user?.role === 'teacher' || user?.role === 'admin') && (
              <TabsContent value="results" className="mt-6">
                <h2 className="text-2xl font-bold mb-6">Test Results</h2>
                
                <div className="space-y-4">
                  {attempts.filter(a => a.status === 'completed').map((attempt) => {
                    const testSeriesItem = testSeries.find(ts => ts.testSeriesId === attempt.testSeriesId);
                    const percentage = Math.round((attempt.score / attempt.totalQuestions) * 100);
                    
                    return (
                      <Card key={attempt.attemptId}>
                        <CardContent className="p-6">
                          <div className="flex justify-between items-center">
                            <div>
                              <h3 className="font-semibold">{testSeriesItem?.title || 'Unknown Test'}</h3>
                              <p className="text-gray-600">Student: {attempt.studentName}</p>
                              <p className="text-sm text-gray-500">
                                Completed: {new Date(attempt.completedAt).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold">{attempt.score}/{attempt.totalQuestions}</div>
                              <div className={`text-lg ${percentage >= 60 ? 'text-green-600' : 'text-red-600'}`}>
                                {percentage}%
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>
            )}

            {(user?.role === 'teacher' || user?.role === 'admin') && (
              <TabsContent value="analytics" className="mt-6">
                <h2 className="text-2xl font-bold mb-6">Analytics</h2>
                
                {analytics && user?.role === 'teacher' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>Total Test Series</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{analytics.totalTestSeries}</div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader>
                          <CardTitle>Total Attempts</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{analytics.totalAttempts}</div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader>
                          <CardTitle>Average Score</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{analytics.averageScore?.toFixed(1) || '0'}</div>
                        </CardContent>
                      </Card>
                    </div>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle>Test Series Performance</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {analytics.testSeriesStats?.map((stat) => (
                            <div key={stat.testSeriesId} className="flex justify-between items-center p-4 border rounded">
                              <div>
                                <h4 className="font-medium">{stat.title}</h4>
                                <p className="text-sm text-gray-600">{stat.attempts} attempts</p>
                              </div>
                              <div className="text-right">
                                <div className="text-lg font-semibold">
                                  Avg: {stat.averageScore?.toFixed(1) || '0'}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </TabsContent>
            )}

            {user?.role === 'admin' && (
              <TabsContent value="users" className="mt-6">
                <h2 className="text-2xl font-bold mb-6">User Management</h2>
                
                <div className="space-y-4">
                  {users.map((userData) => (
                    <Card key={userData.userId}>
                      <CardContent className="p-6">
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="font-semibold">{userData.name}</h3>
                            <p className="text-gray-600">@{userData.username}</p>
                            <p className="text-sm text-gray-500">
                              Joined: {new Date(userData.createdAt).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge variant={userData.role === 'admin' ? 'destructive' : userData.role === 'teacher' ? 'secondary' : 'default'}>
                            {userData.role.toUpperCase()}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            )}
          </Tabs>
        </div>
      </div>
    );
  };

  // Main App Render
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthComponent />;
  }

  if (currentTest && currentAttempt) {
    return <TestTakingComponent />;
  }

  return <Dashboard />;
}