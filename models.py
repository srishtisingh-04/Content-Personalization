from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='learner')  # learner, admin
    interests = db.Column(db.Text)  # JSON string of interests
    skill_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_interests(self):
        if self.interests:
            return json.loads(self.interests)
        return []
    
    def set_interests(self, interests_list):
        self.interests = json.dumps(interests_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'interests': self.get_interests(),
            'skill_level': self.skill_level,
            'created_at': self.created_at.isoformat()
        }

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), default='beginner')
    duration_hours = db.Column(db.Float, default=0)
    instructor = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    quizzes = db.relationship('Quiz', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'duration_hours': self.duration_hours,
            'instructor': self.instructor,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'lesson_count': len(self.lessons),
            'enrollment_count': len(self.enrollments)
        }

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    progress = db.relationship('LessonProgress', backref='lesson', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'content': self.content,
            'order_index': self.order_index,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat()
        }

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    total_questions = db.Column(db.Integer, default=0)
    passing_score = db.Column(db.Integer, default=70)  # percentage
    time_limit_minutes = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'total_questions': self.total_questions,
            'passing_score': self.passing_score,
            'time_limit_minutes': self.time_limit_minutes,
            'created_at': self.created_at.isoformat()
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON string of options
    correct_answer = db.Column(db.Integer, nullable=False)  # index of correct option
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=1)
    
    def get_options(self):
        if self.options:
            return json.loads(self.options)
        return []
    
    def set_options(self, options_list):
        self.options = json.dumps(options_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'options': self.get_options(),
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'points': self.points
        }

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    progress_percentage = db.Column(db.Float, default=0)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress_percentage': self.progress_percentage
        }

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent_minutes = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed_at': self.completed_at.isoformat(),
            'time_spent_minutes': self.time_spent_minutes
        }

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0)
    passed = db.Column(db.Boolean, default=False)
    time_taken_minutes = db.Column(db.Integer, default=0)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.Text)  # JSON string of user answers
    
    def get_answers(self):
        if self.answers:
            return json.loads(self.answers)
        return {}
    
    def set_answers(self, answers_dict):
        self.answers = json.dumps(answers_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'percentage': self.percentage,
            'passed': self.passed,
            'time_taken_minutes': self.time_taken_minutes,
            'attempted_at': self.attempted_at.isoformat(),
            'answers': self.get_answers()
        }
