#!/usr/bin/env python3
"""
Initialize the database with sample data
Run this script to populate the database with courses, lessons, and quizzes
"""
from app import app, db
from models import User, Course, Lesson, Quiz, Question
from werkzeug.security import generate_password_hash

def create_sample_data():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if users exist
        if User.query.count() == 0:
            print("Creating users...")
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
        
        # Check if courses exist
        if Course.query.count() == 0:
            print("Creating courses...")
            
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
        
        # Create lessons
        python_course = Course.query.filter_by(title='Python Programming Fundamentals').first()
        flask_course = Course.query.filter_by(title='Web Development with Flask').first()
        
        if python_course and Lesson.query.filter_by(course_id=python_course.id).count() == 0:
            print("Creating lessons...")
            
            lesson1 = Lesson(
                course_id=python_course.id,
                title='Introduction to Python',
                content='Python is a high-level programming language known for its simplicity and readability. In this lesson, you will learn about Python history, features, and why it is popular among developers.',
                order_index=1,
                duration_minutes=45
            )
            db.session.add(lesson1)
            
            lesson2 = Lesson(
                course_id=python_course.id,
                title='Variables and Data Types',
                content='Learn about Python variables and different data types including integers, floats, strings, booleans, lists, tuples, and dictionaries.',
                order_index=2,
                duration_minutes=60
            )
            db.session.add(lesson2)
            
            lesson3 = Lesson(
                course_id=python_course.id,
                title='Control Structures',
                content='Master if statements, loops (for and while), and how to control the flow of your Python programs.',
                order_index=3,
                duration_minutes=75
            )
            db.session.add(lesson3)
            
            db.session.commit()
            print("✓ Lessons created")
        
        # Create quiz
        if python_course and Quiz.query.filter_by(course_id=python_course.id).count() == 0:
            print("Creating quiz...")
            
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
            db.session.add(q1)
            
            q2 = Question(
                quiz_id=quiz.id,
                question_text='Which of the following is NOT a Python data type?',
                correct_answer=3,
                explanation='Python does not have a separate char type. Characters are strings of length 1.',
                points=1
            )
            q2.set_options(['int', 'float', 'string', 'char'])
            db.session.add(q2)
            
            q3 = Question(
                quiz_id=quiz.id,
                question_text='How do you create a list in Python?',
                correct_answer=0,
                explanation='Lists are created using square brackets [].',
                points=1
            )
            q3.set_options(['list = []', 'list = ()', 'list = {}', 'list = <>'])
            db.session.add(q3)
            
            quiz.total_questions = 3
            db.session.commit()
            print("✓ Quiz and questions created")
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZED SUCCESSFULLY!")
        print("="*60)
        print("\nDefault Accounts:")
        print("  Admin - username: 'admin', password: 'admin123'")
        print("  Learner - username: 'learner', password: 'learner123'")
        print("\nGo to http://localhost:5000 to test!")
        print("="*60)

if __name__ == '__main__':
    create_sample_data()
