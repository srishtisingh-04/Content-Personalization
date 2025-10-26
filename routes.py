from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Course, Lesson, Quiz, Question, Enrollment, LessonProgress, QuizAttempt
from datetime import datetime
import json
from ai_features import (
    generate_course_summary,
    generate_quiz_question,
    analyze_learning_style,
    generate_personalized_path,
    get_learning_insights,
    analyze_quiz_performance
)

auth_bp = Blueprint('auth', __name__)
courses_bp = Blueprint('courses', __name__)
admin_bp = Blueprint('admin', __name__)
learner_bp = Blueprint('learner', __name__)
ai_bp = Blueprint('ai', __name__)

# Authentication Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'learner'),
        skill_level=data.get('skill_level', 'beginner')
    )
    user.set_interests(data.get('interests', []))
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'interests' in data:
        user.set_interests(data['interests'])
    if 'skill_level' in data:
        user.skill_level = data['skill_level']
    if 'email' in data:
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    })

# Course Routes
@courses_bp.route('/', methods=['GET'])
def get_courses():
    try:
        courses = Course.query.all()
        print(f"Found {len(courses)} courses")
        courses_data = [course.to_dict() for course in courses]
        return jsonify(courses_data)
    except Exception as e:
        print(f"Error in get_courses: {str(e)}")
        return jsonify({'error': str(e), 'courses': []}), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    course_data = course.to_dict()
    course_data['lessons'] = [lesson.to_dict() for lesson in course.lessons]
    course_data['quizzes'] = [quiz.to_dict() for quiz in course.quizzes]
    
    return jsonify(course_data)

@courses_bp.route('/category/<category>', methods=['GET'])
def get_courses_by_category(category):
    courses = Course.query.filter_by(category=category).all()
    return jsonify([course.to_dict() for course in courses])

# Learner Routes
@learner_bp.route('/enroll/<int:course_id>', methods=['POST'])
@jwt_required()
def enroll_course(course_id):
    try:
        user_id = get_jwt_identity()
        print(f"Enrollment request: user_id={user_id}, course_id={course_id}")
        
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if existing_enrollment:
            print("Already enrolled")
            return jsonify({'error': 'Already enrolled in this course'}), 400
        
        course = Course.query.get(course_id)
        if not course:
            print("Course not found")
            return jsonify({'error': 'Course not found'}), 404
        
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        
        print("Enrollment successful")
        return jsonify({
            'message': 'Successfully enrolled in course',
            'enrollment': enrollment.to_dict()
        })
    except Exception as e:
        print(f"Enrollment error: {str(e)}")
        return jsonify({'error': f'Enrollment failed: {str(e)}'}), 500

@learner_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    user_id = get_jwt_identity()
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    courses_data = []
    for enrollment in enrollments:
        course_data = enrollment.course.to_dict()
        course_data['enrollment'] = enrollment.to_dict()
        courses_data.append(course_data)
    
    return jsonify(courses_data)

@learner_bp.route('/lesson-progress', methods=['POST'])
@jwt_required()
def mark_lesson_complete():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    lesson_id = data.get('lesson_id')
    time_spent = data.get('time_spent_minutes', 0)
    
    if not lesson_id:
        return jsonify({'error': 'Lesson ID required'}), 400
    
    # Check if already completed
    existing_progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if existing_progress:
        return jsonify({'error': 'Lesson already completed'}), 400
    
    progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, time_spent_minutes=time_spent)
    db.session.add(progress)
    
    # Update course progress
    lesson = Lesson.query.get(lesson_id)
    if lesson:
        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=lesson.course_id).first()
        if enrollment:
            total_lessons = len(lesson.course.lessons)
            completed_lessons = LessonProgress.query.join(Lesson).filter(
                LessonProgress.user_id == user_id,
                Lesson.course_id == lesson.course_id
            ).count()
            enrollment.progress_percentage = (completed_lessons / total_lessons) * 100
            
            if enrollment.progress_percentage >= 100:
                enrollment.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Lesson marked as complete',
        'progress': progress.to_dict()
    })

@learner_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    quiz_data = quiz.to_dict()
    quiz_data['questions'] = [question.to_dict() for question in quiz.questions]
    
    return jsonify(quiz_data)

@learner_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    answers = data.get('answers', {})
    time_taken = data.get('time_taken_minutes', 0)
    
    # Calculate score
    correct_answers = 0
    total_questions = len(quiz.questions)
    
    for question in quiz.questions:
        user_answer = answers.get(str(question.id))
        if user_answer == question.correct_answer:
            correct_answers += 1
    
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = percentage >= quiz.passing_score
    
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=correct_answers,
        total_questions=total_questions,
        correct_answers=correct_answers,
        percentage=percentage,
        passed=passed,
        time_taken_minutes=time_taken
    )
    attempt.set_answers(answers)
    
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({
        'message': 'Quiz submitted successfully',
        'attempt': attempt.to_dict()
    })

@learner_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's interests and completed courses
    user_interests = user.get_interests()
    completed_courses = db.session.query(Course).join(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.completed_at.isnot(None)
    ).all()
    
    # Get courses in user's interest areas
    recommended_courses = []
    if user_interests:
        for interest in user_interests:
            courses = Course.query.filter(Course.category.ilike(f'%{interest}%')).limit(3).all()
            recommended_courses.extend(courses)
    
    # Remove duplicates and already enrolled courses
    enrolled_course_ids = [e.course_id for e in Enrollment.query.filter_by(user_id=user_id).all()]
    recommended_courses = [c for c in recommended_courses if c.id not in enrolled_course_ids]
    
    # Remove duplicates
    seen = set()
    unique_courses = []
    for course in recommended_courses:
        if course.id not in seen:
            seen.add(course.id)
            unique_courses.append(course)
    
    return jsonify([course.to_dict() for course in unique_courses[:6]])

@learner_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        user_id = get_jwt_identity()
        print(f"Dashboard request for user: {user_id}")
        
        # Get user's enrollments
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        print(f"User has {len(enrollments)} enrollments")
        
        # Get recent quiz attempts
        recent_attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(
            QuizAttempt.attempted_at.desc()
        ).limit(5).all()
        
        # Calculate statistics
        total_courses = len(enrollments)
        completed_courses = len([e for e in enrollments if e.completed_at])
        total_quizzes_taken = len(QuizAttempt.query.filter_by(user_id=user_id).all())
        passed_quizzes = len(QuizAttempt.query.filter_by(user_id=user_id, passed=True).all())
        
        # Prepare enrollments with course data
        enrollments_data = []
        for enrollment in enrollments:
            try:
                enrollment_dict = enrollment.to_dict()
                enrollment_dict['course'] = enrollment.course.to_dict()
                enrollments_data.append(enrollment_dict)
            except Exception as e:
                print(f"Error processing enrollment {enrollment.id}: {str(e)}")
        
        return jsonify({
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'total_quizzes_taken': total_quizzes_taken,
            'passed_quizzes': passed_quizzes,
            'recent_attempts': [attempt.to_dict() for attempt in recent_attempts],
            'enrollments': enrollments_data
        })
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'total_courses': 0,
            'completed_courses': 0,
            'total_quizzes_taken': 0,
            'passed_quizzes': 0,
            'recent_attempts': [],
            'enrollments': []
        }), 500

# Admin Routes
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@admin_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    course = Course(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        difficulty_level=data.get('difficulty_level', 'beginner'),
        duration_hours=data.get('duration_hours', 0),
        instructor=data.get('instructor', '')
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({
        'message': 'Course created successfully',
        'course': course.to_dict()
    }), 201

@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    data = request.get_json()
    
    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.category = data.get('category', course.category)
    course.difficulty_level = data.get('difficulty_level', course.difficulty_level)
    course.duration_hours = data.get('duration_hours', course.duration_hours)
    course.instructor = data.get('instructor', course.instructor)
    course.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Course updated successfully',
        'course': course.to_dict()
    })

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({'message': 'Course deleted successfully'})

@admin_bp.route('/courses/<int:course_id>/lessons', methods=['POST'])
@jwt_required()
def create_lesson(course_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    data = request.get_json()
    
    lesson = Lesson(
        course_id=course_id,
        title=data['title'],
        content=data['content'],
        order_index=data.get('order_index', 0),
        duration_minutes=data.get('duration_minutes', 0)
    )
    
    db.session.add(lesson)
    db.session.commit()
    
    return jsonify({
        'message': 'Lesson created successfully',
        'lesson': lesson.to_dict()
    }), 201

@admin_bp.route('/courses/<int:course_id>/quizzes', methods=['POST'])
@jwt_required()
def create_quiz(course_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    data = request.get_json()
    
    quiz = Quiz(
        course_id=course_id,
        title=data['title'],
        description=data.get('description', ''),
        passing_score=data.get('passing_score', 70),
        time_limit_minutes=data.get('time_limit_minutes', 30)
    )
    
    db.session.add(quiz)
    db.session.commit()
    
    return jsonify({
        'message': 'Quiz created successfully',
        'quiz': quiz.to_dict()
    }), 201

@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
def create_question(quiz_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    data = request.get_json()
    
    question = Question(
        quiz_id=quiz_id,
        question_text=data['question_text'],
        correct_answer=data['correct_answer'],
        explanation=data.get('explanation', ''),
        points=data.get('points', 1)
    )
    question.set_options(data['options'])
    
    db.session.add(question)
    
    # Update quiz total questions count
    quiz.total_questions = len(quiz.questions) + 1
    
    db.session.commit()
    
    return jsonify({
        'message': 'Question created successfully',
        'question': question.to_dict()
    }), 201

@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get analytics data
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    total_quiz_attempts = QuizAttempt.query.count()
    
    # Course performance
    courses = Course.query.all()
    course_performance = []
    for course in courses:
        enrollments = len(course.enrollments)
        completions = len([e for e in course.enrollments if e.completed_at])
        completion_rate = (completions / enrollments * 100) if enrollments > 0 else 0
        
        course_performance.append({
            'course_id': course.id,
            'title': course.title,
            'enrollments': enrollments,
            'completions': completions,
            'completion_rate': completion_rate
        })
    
    return jsonify({
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_quiz_attempts': total_quiz_attempts,
        'course_performance': course_performance
    })

# AI Routes
@ai_bp.route('/summarize-course/<int:course_id>', methods=['GET'])
@jwt_required()
def summarize_course(course_id):
    """Generate AI summary of a course"""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Combine all course content
    content = course.description
    for lesson in course.lessons:
        content += " " + (lesson.content or "")
    
    summary = generate_course_summary(content)
    
    return jsonify({
        'course_id': course_id,
        'course_title': course.title,
        'ai_summary': summary
    })

@ai_bp.route('/analyze-learning-style', methods=['GET'])
@jwt_required()
def analyze_user_learning_style():
    """Analyze user's learning style based on their activity"""
    user_id = get_jwt_identity()
    
    # Get user's quiz attempts
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    
    # Get lesson progress
    lesson_progress = LessonProgress.query.filter_by(user_id=user_id).all()
    completion_times = [p.time_spent_minutes for p in lesson_progress]
    
    analysis = analyze_learning_style(
        [{'score': attempt.score, 'percentage': attempt.percentage} for attempt in quiz_attempts],
        completion_times
    )
    
    return jsonify(analysis)

@ai_bp.route('/personalized-path', methods=['GET'])
@jwt_required()
def get_personalized_path():
    """Get AI-recommended personalized learning path"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's enrollments
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    completed_course_ids = [e.course_id for e in enrollments if e.completed_at]
    completed_courses = Course.query.filter(Course.id.in_(completed_course_ids)).all()
    
    # Get all available courses
    all_courses = Course.query.all()
    
    # Generate personalized path
    recommendations = generate_personalized_path(
        user_profile={
            'interests': user.get_interests(),
            'skill_level': user.skill_level
        },
        completed_courses=completed_courses,
        all_courses=all_courses
    )
    
    return jsonify({
        'recommended_path': [{
            'course': rec['course'].to_dict(),
            'score': rec['score'],
            'reason': rec['reason']
        } for rec in recommendations]
    })

@ai_bp.route('/learning-insights', methods=['GET'])
@jwt_required()
def get_user_insights():
    """Get AI-powered learning insights for the user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's enrollments
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    courses = [e.course for e in enrollments]
    
    # Get quiz attempts
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    
    # Get lesson progress
    lesson_progress = LessonProgress.query.filter_by(user_id=user_id).all()
    
    insights = get_learning_insights(user_id, courses, quiz_attempts, lesson_progress)
    
    # Analyze performance
    performance = analyze_quiz_performance(quiz_attempts)
    
    return jsonify({
        'insights': insights,
        'performance_analysis': performance
    })

@ai_bp.route('/generate-quiz', methods=['POST'])
@jwt_required()
def generate_ai_quiz():
    """Generate AI-powered quiz from course content"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    course_id = data.get('course_id')
    difficulty = data.get('difficulty', 'intermediate')
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Generate questions for each lesson
    generated_questions = []
    for lesson in course.lessons:
        if lesson.content:
            question = generate_quiz_question(lesson.content, difficulty)
            if question:
                generated_questions.append({
                    'lesson_id': lesson.id,
                    'question': question
                })
    
    return jsonify({
        'course_id': course_id,
        'difficulty': difficulty,
        'generated_questions': generated_questions
    })

# Register blueprints
def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(learner_bp, url_prefix='/api/learner')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
