# LearnSmart - Personalized Learning Platform

A full-stack web application for personalized learning with AI-powered insights, course recommendations, and interactive quizzes.

## 🌟 Features

### For Learners:
- User registration and JWT authentication
- Personalized course recommendations based on interests
- Interactive quizzes with scoring
- AI-powered learning insights
- Progress tracking dashboard
- Course browsing and enrollment

### For Admins:
- Course and user management
- Quiz creation and management
- Analytics dashboard
- Content management system

### AI Features:
- Personalized learning path recommendations
- Learning style analysis
- Performance insights
- Smart course suggestions

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd learnsmart
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
The database will be automatically created when you run the app for the first time.

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Application
Open your browser and go to: `http://localhost:5000`

## 📝 Default Accounts

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Learner Account:**
- Username: `learner`
- Password: `learner123`

## 🛠 Tech Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend:** Python Flask
- **Database:** SQLite
- **Authentication:** JWT (JSON Web Tokens)

## 📁 Project Structure

```
learnsmart/
├── app.py                 # Main application file
├── models.py              # Database models
├── routes.py              # API routes and endpoints
├── ai_features.py         # AI functionality
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── app.js          # Frontend JavaScript
└── README.md              # This file
```

## 🎯 Usage

1. **Register/Login** - Create an account or use default credentials
2. **Browse Courses** - Explore available courses
3. **Enroll** - Enroll in courses of interest
4. **Take Quizzes** - Test your knowledge
5. **Dashboard** - Track your progress and get AI insights
6. **AI Recommendations** - Get personalized course suggestions

## 🤖 AI Features

- **Learning Insights:** Get AI-powered feedback on your progress
- **Personalized Recommendations:** Courses tailored to your interests
- **Performance Analysis:** Understand your strengths and areas for improvement
- **Smart Learning Paths:** Suggested course progression

## 📄 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Courses
- `GET /api/courses/` - Get all courses
- `GET /api/courses/<id>` - Get course details

### Learner
- `POST /api/learner/enroll/<course_id>` - Enroll in course
- `GET /api/learner/dashboard` - Get dashboard data
- `GET /api/learner/recommendations` - Get recommendations
- `GET /api/learner/quiz/<quiz_id>` - Get quiz
- `POST /api/learner/quiz/<quiz_id>/submit` - Submit quiz

### AI
- `GET /api/ai/learning-insights` - Get AI insights
- `GET /api/ai/personalized-path` - Get learning path
- `GET /api/ai/analyze-learning-style` - Analyze learning style

### Admin
- `GET /api/admin/users` - Get all users
- `POST /api/admin/courses` - Create course
- `DELETE /api/admin/courses/<id>` - Delete course
- `GET /api/admin/analytics` - Get analytics

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Database
The app uses SQLite by default. The database file is created automatically in the `instance/` folder.

## 📝 License

MIT License - Feel free to use this project for learning and development!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub.
