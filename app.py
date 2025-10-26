from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///learnsmart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

# Import models first to get db instance
from models import db
db.init_app(app)

jwt = JWTManager(app)
CORS(app)

# Import routes after db initialization
from routes import register_routes

# Register all routes
register_routes(app)

@app.route('/')
def index():
    return render_template('index.html')

def initialize_db():
    """Initialize database with sample data if empty"""
    with app.app_context():
        db.create_all()
        
        # Check if database is empty
        from models import User, Course
        user_count = User.query.count()
        course_count = Course.query.count()
        
        # If no users or courses, initialize sample data
        if user_count == 0 or course_count == 0:
            print("Initializing database with sample data...")
            
            from werkzeug.security import generate_password_hash
            from models import Lesson, Quiz, Question
            
            # Create users if they don't exist
            if user_count == 0:
                admin_user = User(
                    username='admin',
                    email='admin@learnsmart.com',
                    role='admin',
                    skill_level='advanced'
                )
                admin_user.password_hash = generate_password_hash('admin123')
                
                learner_user = User(
                    username='learner',
                    email='learner@learnsmart.com',
                    role='learner',
                    skill_level='beginner'
                )
                learner_user.password_hash = generate_password_hash('learner123')
                learner_user.set_interests(['programming', 'web development', 'python'])
                
                db.session.add(admin_user)
                db.session.add(learner_user)
                db.session.commit()
                print("✓ Users created")
            
            # Create courses if they don't exist
            if course_count == 0:
                # Create Python Course
                python_course = Course(
                    title='Python Programming Fundamentals',
                    description='Learn the basics of Python programming language from scratch. Perfect for beginners.',
                    category='programming',
                    difficulty_level='beginner',
                    duration_hours=20.0,
                    instructor='Dr. Sarah Johnson'
                )
                db.session.add(python_course)
                db.session.commit()
                
                # Create Flask Course
                flask_course = Course(
                    title='Web Development with Flask',
                    description='Build web applications using Python Flask framework.',
                    category='web development',
                    difficulty_level='intermediate',
                    duration_hours=25.0,
                    instructor='Prof. Michael Chen'
                )
                db.session.add(flask_course)
                db.session.commit()
                
                # Create Database Course
                db_course = Course(
                    title='Database Design and Management',
                    description='Learn how to design and manage databases effectively.',
                    category='database',
                    difficulty_level='intermediate',
                    duration_hours=18.0,
                    instructor='Dr. Emily Rodriguez'
                )
                db.session.add(db_course)
                db.session.commit()
                
                # Create Machine Learning Course
                ml_course = Course(
                    title='Machine Learning Basics',
                    description='Introduction to machine learning concepts and algorithms.',
                    category='machine learning',
                    difficulty_level='advanced',
                    duration_hours=30.0,
                    instructor='Dr. James Wilson'
                )
                db.session.add(ml_course)
                db.session.commit()
                
                # Create Bootstrap Course
                bs_course = Course(
                    title='Frontend Development with Bootstrap',
                    description='Create responsive web designs using Bootstrap framework.',
                    category='web development',
                    difficulty_level='beginner',
                    duration_hours=15.0,
                    instructor='Ms. Lisa Thompson'
                )
                db.session.add(bs_course)
                db.session.commit()
                
                print("✓ Courses created")
                
                # Create lessons for Python course
                python_course = Course.query.filter_by(title='Python Programming Fundamentals').first()
                lesson1 = Lesson(
                    course_id=python_course.id,
                    title='Introduction to Python',
                    content='Python is a high-level programming language known for its simplicity and readability. In this lesson, you will learn about Python history, features, and why it is popular among developers.',
                    order_index=1,
                    duration_minutes=45
                )
                lesson2 = Lesson(
                    course_id=python_course.id,
                    title='Variables and Data Types',
                    content='Learn about Python variables and different data types including integers, floats, strings, booleans, lists, tuples, and dictionaries.',
                    order_index=2,
                    duration_minutes=60
                )
                lesson3 = Lesson(
                    course_id=python_course.id,
                    title='Control Structures',
                    content='Master if statements, loops (for and while), and how to control the flow of your Python programs.',
                    order_index=3,
                    duration_minutes=75
                )
                db.session.add(lesson1)
                db.session.add(lesson2)
                db.session.add(lesson3)
                db.session.commit()
                
                # Create quiz for Python course
                quiz = Quiz(
                    course_id=python_course.id,
                    title='Python Fundamentals Quiz',
                    description='Test your knowledge of Python programming basics',
                    passing_score=70,
                    time_limit_minutes=30
                )
                db.session.add(quiz)
                db.session.commit()
                
                # Create questions
                q1 = Question(
                    quiz_id=quiz.id,
                    question_text='What is the correct way to create a variable in Python?',
                    correct_answer=1,
                    explanation='In Python, you simply assign a value to a variable name without declaring the type.',
                    points=1
                )
                q1.set_options(['var x = 5', 'x = 5', 'int x = 5', 'variable x = 5'])
                
                q2 = Question(
                    quiz_id=quiz.id,
                    question_text='Which of the following is NOT a Python data type?',
                    correct_answer=3,
                    explanation='Python does not have a separate char type. Characters are strings of length 1.',
                    points=1
                )
                q2.set_options(['int', 'float', 'string', 'char'])
                
                db.session.add(q1)
                db.session.add(q2)
                quiz.total_questions = 2
                db.session.commit()
                
                print("✓ Lessons and quiz created")
                
                print("\n" + "="*60)
                print("✓ Database initialized successfully!")
                print("Default accounts created:")
                print("  Admin: username='admin', password='admin123'")
                print("  Learner: username='learner', password='learner123'")
                print("="*60)

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
