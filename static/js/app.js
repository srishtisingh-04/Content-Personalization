// LearnSmart Frontend JavaScript

// Global variables
let currentUser = null;
let currentCourse = null;
let currentQuiz = null;
let quizAnswers = {};
let quizTimer = null;
let timeRemaining = 0;

// API Base URL
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('LearnSmart app initialized');
    checkAuthStatus();
    setupEventListeners();
});

// Check if user is authenticated
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    if (token) {
        // Verify token and get user info
        fetch(`${API_BASE}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                localStorage.removeItem('access_token');
                throw new Error('Invalid token');
            }
        })
        .then(user => {
            currentUser = user;
            updateUIForLoggedInUser();
        })
        .catch(error => {
            console.error('Auth check failed:', error);
            updateUIForLoggedOutUser();
        });
    } else {
        updateUIForLoggedOutUser();
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser() {
    document.getElementById('loginLink').style.display = 'none';
    document.getElementById('registerLink').style.display = 'none';
    document.getElementById('userMenu').style.display = 'block';
    document.getElementById('dashboardLink').style.display = 'block';
    document.getElementById('usernameDisplay').textContent = currentUser.username;
    
    if (currentUser.role === 'admin') {
        document.getElementById('adminLink').style.display = 'block';
    }
}

// Update UI for logged out user
function updateUIForLoggedOutUser() {
    document.getElementById('loginLink').style.display = 'block';
    document.getElementById('registerLink').style.display = 'block';
    document.getElementById('userMenu').style.display = 'none';
    document.getElementById('dashboardLink').style.display = 'none';
    document.getElementById('adminLink').style.display = 'none';
    currentUser = null;
}

// Setup event listeners
function setupEventListeners() {
    console.log('Setting up event listeners');
    
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('Login form event listener added');
    } else {
        console.error('Login form not found');
    }
    
    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        console.log('Register form event listener added');
    } else {
        console.error('Register form not found');
    }
    
    // Create course form
    const createCourseForm = document.getElementById('createCourseForm');
    if (createCourseForm) {
        createCourseForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createCourse();
        });
        console.log('Create course form event listener added');
    }
}

// Show different sections
function showHome() {
    hideAllSections();
    document.getElementById('homeSection').style.display = 'block';
}

function showLogin() {
    hideAllSections();
    document.getElementById('loginSection').style.display = 'block';
}

function showRegister() {
    hideAllSections();
    document.getElementById('registerSection').style.display = 'block';
}

function showCourses() {
    hideAllSections();
    document.getElementById('coursesSection').style.display = 'block';
    loadCourses();
}

function showDashboard() {
    if (!currentUser) {
        showLogin();
        return;
    }
    hideAllSections();
    document.getElementById('dashboardSection').style.display = 'block';
    loadDashboard();
}

function showAdmin() {
    if (!currentUser || currentUser.role !== 'admin') {
        showAlert('Access denied. Admin privileges required.', 'danger');
        return;
    }
    hideAllSections();
    document.getElementById('adminSection').style.display = 'block';
    loadAdminData();
}

function showProfile() {
    showAlert('Profile management coming soon!', 'info');
}

function showCourseDetail(courseId) {
    hideAllSections();
    document.getElementById('courseDetailSection').style.display = 'block';
    loadCourseDetail(courseId);
}

function showQuiz(quizId) {
    hideAllSections();
    document.getElementById('quizSection').style.display = 'block';
    loadQuiz(quizId);
}

// Hide all sections
function hideAllSections() {
    const sections = ['homeSection', 'loginSection', 'registerSection', 'coursesSection', 
                     'dashboardSection', 'adminSection', 'courseDetailSection', 'quizSection'];
    sections.forEach(section => {
        document.getElementById(section).style.display = 'none';
    });
}

// Handle login
function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    console.log('Logging in user:', username);
    
    fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => {
        console.log('Login response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Login response data:', data);
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            currentUser = data.user;
            updateUIForLoggedInUser();
            showAlert('Login successful!', 'success');
            showHome();
        } else {
            showAlert(data.error || 'Login failed', 'danger');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showAlert('Login failed. Please try again.', 'danger');
    });
}

// Handle register
function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const skillLevel = document.getElementById('regSkillLevel').value;
    const interestsText = document.getElementById('regInterests').value;
    const interests = interestsText ? interestsText.split(',').map(i => i.trim()).filter(i => i) : [];
    
    console.log('Registering user:', { username, email, skillLevel, interests });
    
    fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username,
            email,
            password,
            skill_level: skillLevel,
            interests: interests
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            currentUser = data.user;
            updateUIForLoggedInUser();
            showAlert('Registration successful!', 'success');
            showHome();
        } else {
            showAlert(data.error || 'Registration failed', 'danger');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        showAlert('Registration failed. Please try again.', 'danger');
    });
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    currentUser = null;
    updateUIForLoggedOutUser();
    showAlert('Logged out successfully', 'info');
    showHome();
}

// Load courses
function loadCourses() {
    console.log('Loading courses...');
    fetch(`${API_BASE}/courses/`)
    .then(response => {
        console.log('Courses response status:', response.status);
        if (!response.ok) {
            console.error('Response not OK:', response.status);
        }
        return response.json();
    })
    .then(courses => {
        console.log('Courses received:', courses.length, 'courses');
        const coursesList = document.getElementById('coursesList');
        coursesList.innerHTML = '';
        
        if (!courses || courses.length === 0) {
            coursesList.innerHTML = `
                <div class="col-12">
                    <div class="card">
                        <div class="card-body text-center">
                            <i class="fas fa-book fa-3x text-muted mb-3"></i>
                            <h5 class="card-title">No courses available</h5>
                            <p class="card-text">Please run <code>python setup_db.py</code> to initialize the database with sample courses.</p>
                            <button class="btn btn-primary" onclick="showHome()">Go to Home</button>
                        </div>
                    </div>
                </div>
            `;
            return;
        }
        
        courses.forEach(course => {
            const courseCard = createCourseCard(course);
            coursesList.appendChild(courseCard);
        });
    })
    .catch(error => {
        console.error('Failed to load courses:', error);
        const coursesList = document.getElementById('coursesList');
        coursesList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <h5>Failed to load courses</h5>
                    <p>Error: ${error.message}</p>
                    <p class="small">Make sure you have run <code>python setup_db.py</code> to initialize the database.</p>
                </div>
            </div>
        `;
    });
}

// Create course card
function createCourseCard(course) {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-4';
    
    col.innerHTML = `
        <div class="card course-card h-100" onclick="showCourseDetail(${course.id})">
            <div class="card-body">
                <h5 class="card-title">${course.title}</h5>
                <p class="card-text">${course.description || 'No description available'}</p>
                <div class="mb-2">
                    <span class="badge bg-primary">${course.category}</span>
                    <span class="badge bg-secondary">${course.difficulty_level}</span>
                </div>
                <small class="text-muted">
                    <i class="fas fa-clock"></i> ${course.duration_hours}h | 
                    <i class="fas fa-book"></i> ${course.lesson_count} lessons |
                    <i class="fas fa-users"></i> ${course.enrollment_count} enrolled
                </small>
            </div>
        </div>
    `;
    
    return col;
}

// Load course detail
function loadCourseDetail(courseId) {
    fetch(`${API_BASE}/courses/${courseId}`)
    .then(response => response.json())
    .then(course => {
        currentCourse = course;
        const content = document.getElementById('courseDetailContent');
        
        content.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h2>${course.title}</h2>
                    <p class="lead">${course.description}</p>
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <strong>Category:</strong> ${course.category}
                        </div>
                        <div class="col-md-3">
                            <strong>Difficulty:</strong> ${course.difficulty_level}
                        </div>
                        <div class="col-md-3">
                            <strong>Duration:</strong> ${course.duration_hours} hours
                        </div>
                        <div class="col-md-3">
                            <strong>Instructor:</strong> ${course.instructor || 'TBA'}
                        </div>
                    </div>
                    ${currentUser ? `
                        <button class="btn btn-primary enroll-btn" onclick="enrollInCourse(${course.id})">
                            <i class="fas fa-plus"></i> Enroll in Course
                        </button>
                    ` : `
                        <button class="btn btn-primary enroll-btn" onclick="showLogin()">
                            <i class="fas fa-sign-in-alt"></i> Login to Enroll
                        </button>
                    `}
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-8">
                    <h4>Lessons</h4>
                    <div id="lessonsList">
                        ${course.lessons.map(lesson => `
                            <div class="lesson-content">
                                <h5>${lesson.title}</h5>
                                <p>${lesson.content || 'Content coming soon...'}</p>
                                <small class="text-muted">
                                    <i class="fas fa-clock"></i> ${lesson.duration_minutes} minutes
                                </small>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="col-md-4">
                    <h4>Quizzes</h4>
                    <div id="quizzesList">
                        ${course.quizzes.map(quiz => `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6>${quiz.title}</h6>
                                    <p class="small">${quiz.description || 'Test your knowledge'}</p>
                                    <small class="text-muted">
                                        ${quiz.total_questions} questions | 
                                        ${quiz.time_limit_minutes} minutes
                                    </small>
                                    <br>
                                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showQuiz(${quiz.id})">
                                        Take Quiz
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    })
    .catch(error => {
        showAlert('Failed to load course details', 'danger');
    });
}

// Enroll in course
function enrollInCourse(courseId) {
    console.log('Attempting to enroll in course:', courseId);
    
    const token = localStorage.getItem('access_token');
    console.log('Token exists:', !!token);
    
    if (!token) {
        showAlert('Please login to enroll', 'warning');
        showLogin();
        return;
    }
    
    fetch(`${API_BASE}/learner/enroll/${courseId}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Enrollment response status:', response.status);
        console.log('Response headers:', response.headers);
        if (!response.ok) {
            console.error('Response not OK:', response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Enrollment response data:', data);
        if (data.message) {
            showAlert(data.message, 'success');
            // Reload the page to show updated enrollment status
            window.location.reload();
        } else {
            console.error('Enrollment failed, data:', data);
            showAlert(data.error || 'Enrollment failed', 'danger');
        }
    })
    .catch(error => {
        console.error('Enrollment error:', error);
        showAlert('Enrollment failed. Please check console for details.', 'danger');
    });
}

// Load dashboard
function loadDashboard() {
    fetch(`${API_BASE}/learner/dashboard`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update stats
        document.getElementById('totalCourses').textContent = data.total_courses;
        document.getElementById('completedCourses').textContent = data.completed_courses;
        document.getElementById('totalQuizzes').textContent = data.total_quizzes_taken;
        document.getElementById('passedQuizzes').textContent = data.passed_quizzes;
        
        // Load my courses
        const myCoursesList = document.getElementById('myCoursesList');
        myCoursesList.innerHTML = '';
        
        data.enrollments.forEach(enrollment => {
            const courseCard = document.createElement('div');
            courseCard.className = 'card mb-3';
            courseCard.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title">${enrollment.course.title}</h6>
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar" style="width: ${enrollment.progress_percentage}%"></div>
                            </div>
                            <small class="text-muted">${enrollment.progress_percentage.toFixed(1)}% complete</small>
                        </div>
                        <button class="btn btn-sm btn-outline-primary" onclick="showCourseDetail(${enrollment.course.id})">
                            Continue
                        </button>
                    </div>
                </div>
            `;
            myCoursesList.appendChild(courseCard);
        });
        
        // Load recommendations
        loadRecommendations();
        
        // Load AI insights
        loadAIInsights();
    })
    .catch(error => {
        showAlert('Failed to load dashboard', 'danger');
    });
}

// Load AI insights
function loadAIInsights() {
    fetch(`${API_BASE}/ai/learning-insights`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const insightsList = document.getElementById('insightsList');
        insightsList.innerHTML = '';
        
        if (data.insights && data.insights.length > 0) {
            data.insights.forEach(insight => {
                const insightItem = document.createElement('p');
                insightItem.className = 'small mb-2';
                insightItem.textContent = insight;
                insightsList.appendChild(insightItem);
            });
        } else {
            insightsList.innerHTML = '<p class="small text-muted">No insights available yet. Start learning to get personalized insights!</p>';
        }
        
        // Show performance analysis
        if (data.performance_analysis) {
            const perf = data.performance_analysis;
            if (perf.average_score) {
                const scoreInfo = document.createElement('p');
                scoreInfo.className = 'small mt-3 mb-0';
                scoreInfo.innerHTML = `<strong>Average Score:</strong> ${perf.average_score}%`;
                insightsList.appendChild(scoreInfo);
            }
            
            if (perf.recommendations && perf.recommendations.length > 0) {
                perf.recommendations.forEach(rec => {
                    const recItem = document.createElement('p');
                    recItem.className = 'small mb-1';
                    recItem.innerHTML = `💡 ${rec}`;
                    insightsList.appendChild(recItem);
                });
            }
        }
    })
    .catch(error => {
        console.error('Failed to load AI insights:', error);
        document.getElementById('insightsList').innerHTML = '<p class="small text-muted">Unable to load insights at this time.</p>';
    });
}

// Load recommendations
function loadRecommendations() {
    fetch(`${API_BASE}/learner/recommendations`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(courses => {
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = '';
        
        courses.forEach(course => {
            const courseCard = document.createElement('div');
            courseCard.className = 'card recommendation-card';
            courseCard.innerHTML = `
                <div class="card-body">
                    <h6 class="card-title">${course.title}</h6>
                    <p class="card-text small">${course.description || 'No description'}</p>
                    <small class="text-muted">${course.category} • ${course.difficulty_level}</small>
                    <br>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showCourseDetail(${course.id})">
                        View Course
                    </button>
                </div>
            `;
            recommendationsList.appendChild(courseCard);
        });
    })
    .catch(error => {
        console.error('Failed to load recommendations:', error);
    });
}

// Load quiz
function loadQuiz(quizId) {
    fetch(`${API_BASE}/learner/quiz/${quizId}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(quiz => {
        currentQuiz = quiz;
        quizAnswers = {};
        timeRemaining = quiz.time_limit_minutes * 60;
        
        const quizContent = document.getElementById('quizContent');
        quizContent.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3>${quiz.title}</h3>
                    <p>${quiz.description || 'Test your knowledge'}</p>
                    <div class="quiz-timer" id="quizTimer">
                        Time Remaining: <span id="timeDisplay">${formatTime(timeRemaining)}</span>
                    </div>
                </div>
                <div class="card-body">
                    <div id="quizQuestions">
                        ${quiz.questions.map((question, index) => `
                            <div class="quiz-question">
                                <h5>Question ${index + 1}</h5>
                                <p>${question.question_text}</p>
                                <div class="quiz-options">
                                    ${question.options.map((option, optionIndex) => `
                                        <div class="quiz-option" onclick="selectAnswer(${question.id}, ${optionIndex})" data-question="${question.id}" data-option="${optionIndex}">
                                            ${option}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="text-center mt-4">
                        <button class="btn btn-primary btn-lg" onclick="submitQuiz()">
                            Submit Quiz
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Start timer
        startQuizTimer();
    })
    .catch(error => {
        showAlert('Failed to load quiz', 'danger');
    });
}

// Select answer
function selectAnswer(questionId, optionIndex) {
    quizAnswers[questionId] = optionIndex;
    
    // Update UI
    const questionElement = document.querySelector(`[data-question="${questionId}"]`).closest('.quiz-question');
    questionElement.querySelectorAll('.quiz-option').forEach(option => {
        option.classList.remove('selected');
    });
    questionElement.querySelector(`[data-option="${optionIndex}"]`).classList.add('selected');
}

// Start quiz timer
function startQuizTimer() {
    quizTimer = setInterval(() => {
        timeRemaining--;
        document.getElementById('timeDisplay').textContent = formatTime(timeRemaining);
        
        if (timeRemaining <= 0) {
            clearInterval(quizTimer);
            submitQuiz();
        }
    }, 1000);
}

// Format time
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Submit quiz
function submitQuiz() {
    if (quizTimer) {
        clearInterval(quizTimer);
    }
    
    const timeTaken = Math.floor((currentQuiz.time_limit_minutes * 60 - timeRemaining) / 60);
    
    fetch(`${API_BASE}/learner/quiz/${currentQuiz.id}/submit`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            answers: quizAnswers,
            time_taken_minutes: timeTaken
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.attempt) {
            showQuizResults(data.attempt);
        } else {
            showAlert(data.error || 'Quiz submission failed', 'danger');
        }
    })
    .catch(error => {
        showAlert('Quiz submission failed', 'danger');
    });
}

// Show quiz results
function showQuizResults(attempt) {
    const quizContent = document.getElementById('quizContent');
    quizContent.innerHTML = `
        <div class="quiz-results">
            <div class="score-circle ${attempt.passed ? 'score-pass' : 'score-fail'}">
                ${attempt.percentage.toFixed(1)}%
            </div>
            <h3>${attempt.passed ? 'Congratulations!' : 'Keep Learning!'}</h3>
            <p class="lead">
                You scored ${attempt.correct_answers} out of ${attempt.total_questions} questions.
            </p>
            <p>
                Time taken: ${attempt.time_taken_minutes} minutes
            </p>
            <div class="mt-4">
                <button class="btn btn-primary me-2" onclick="showCourseDetail(${currentCourse.id})">
                    Back to Course
                </button>
                <button class="btn btn-outline-primary" onclick="showDashboard()">
                    Dashboard
                </button>
            </div>
        </div>
    `;
}

// Admin functions
function loadAdminData() {
    loadAdminCourses();
    loadUsers();
    loadAnalytics();
}

function loadAdminCourses() {
    fetch(`${API_BASE}/courses/`)
    .then(response => response.json())
    .then(courses => {
        const adminCoursesList = document.getElementById('adminCoursesList');
        adminCoursesList.innerHTML = '';
        
        courses.forEach(course => {
            const courseRow = document.createElement('div');
            courseRow.className = 'card mb-3';
            courseRow.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">${course.title}</h5>
                            <p class="card-text">${course.description || 'No description'}</p>
                            <small class="text-muted">
                                ${course.category} • ${course.difficulty_level} • 
                                ${course.enrollment_count} enrollments
                            </small>
                        </div>
                        <div class="admin-actions">
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editCourse(${course.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteCourse(${course.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
            adminCoursesList.appendChild(courseRow);
        });
    })
    .catch(error => {
        showAlert('Failed to load courses', 'danger');
    });
}

function loadUsers() {
    fetch(`${API_BASE}/admin/users`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(users => {
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '';
        
        users.forEach(user => {
            const userRow = document.createElement('div');
            userRow.className = 'card mb-2';
            userRow.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title">${user.username}</h6>
                            <small class="text-muted">${user.email} • ${user.role}</small>
                        </div>
                        <span class="badge ${user.role === 'admin' ? 'bg-danger' : 'bg-primary'} role-badge">
                            ${user.role}
                        </span>
                    </div>
                </div>
            `;
            usersList.appendChild(userRow);
        });
    })
    .catch(error => {
        showAlert('Failed to load users', 'danger');
    });
}

function loadAnalytics() {
    fetch(`${API_BASE}/admin/analytics`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('totalUsers').textContent = data.total_users;
        document.getElementById('totalCoursesAdmin').textContent = data.total_courses;
        document.getElementById('totalEnrollments').textContent = data.total_enrollments;
        document.getElementById('totalQuizAttempts').textContent = data.total_quiz_attempts;
        
        // Load course performance
        const coursePerformance = document.getElementById('coursePerformance');
        coursePerformance.innerHTML = '';
        
        data.course_performance.forEach(course => {
            const performanceCard = document.createElement('div');
            performanceCard.className = 'card mb-2';
            performanceCard.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title">${course.title}</h6>
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar" style="width: ${course.completion_rate}%"></div>
                            </div>
                            <small class="text-muted">
                                ${course.completions}/${course.enrollments} completed (${course.completion_rate.toFixed(1)}%)
                            </small>
                        </div>
                    </div>
                </div>
            `;
            coursePerformance.appendChild(performanceCard);
        });
    })
    .catch(error => {
        showAlert('Failed to load analytics', 'danger');
    });
}

function showCreateCourseModal() {
    const modal = new bootstrap.Modal(document.getElementById('createCourseModal'));
    modal.show();
}

function createCourse() {
    const title = document.getElementById('courseTitle').value;
    const description = document.getElementById('courseDescription').value;
    const category = document.getElementById('courseCategory').value;
    const difficulty = document.getElementById('courseDifficulty').value;
    const duration = document.getElementById('courseDuration').value;
    const instructor = document.getElementById('courseInstructor').value;
    
    fetch(`${API_BASE}/admin/courses`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title,
            description,
            category,
            difficulty_level: difficulty,
            duration_hours: parseFloat(duration) || 0,
            instructor
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showAlert(data.message, 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('createCourseModal'));
            modal.hide();
            loadAdminCourses();
        } else {
            showAlert(data.error || 'Failed to create course', 'danger');
        }
    })
    .catch(error => {
        showAlert('Failed to create course', 'danger');
    });
}

function editCourse(courseId) {
    showAlert('Edit functionality coming soon!', 'info');
}

function deleteCourse(courseId) {
    if (confirm('Are you sure you want to delete this course?')) {
        fetch(`${API_BASE}/admin/courses/${courseId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showAlert(data.message, 'success');
                loadAdminCourses();
            } else {
                showAlert(data.error || 'Failed to delete course', 'danger');
            }
        })
        .catch(error => {
            showAlert('Failed to delete course', 'danger');
        });
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertId = 'alert-' + Date.now();
    
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Initialize with home page
showHome();
