"""
AI Features for LearnSmart
This module provides AI-powered features including content summarization,
quiz generation, and personalized recommendations.
"""

import re

def generate_course_summary(course_content):
    """
    Generate an AI-powered summary of course content.
    Uses extractive summarization to create concise summaries.
    """
    # Split content into sentences
    sentences = re.split(r'[.!?]+', course_content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return "No content available for summarization."
    
    # Get key sentences - first sentence + important sentences
    summary = sentences[0]
    
    # Add additional sentences for a more complete summary
    for i in range(1, min(3, len(sentences))):
        if i < len(sentences):
            summary += ". " + sentences[i]
    
    return summary

def generate_quiz_question(content, difficulty="intermediate"):
    """
    Generate a quiz question from course content using templates.
    This is a simplified version - in production, you'd use GPT or similar.
    """
    # Extract key concepts
    sentences = re.split(r'[.!?]+', content)
    if not sentences:
        return None
    
    # Simple question generation based on key concepts
    key_concept = sentences[0].split()[0:5]  # First few words
    concept = ' '.join(key_concept)
    
    question_templates = {
        "beginner": f"What is {concept}?",
        "intermediate": f"Which of the following best describes {concept}?",
        "advanced": f"In the context of {concept}, which statement is most accurate?"
    }
    
    question_text = question_templates.get(difficulty, question_templates["intermediate"])
    
    return {
        "question": question_text,
        "options": [
            "Correct answer option",
            "Option 2",
            "Option 3",
            "Option 4"
        ],
        "correct_answer": 0
    }

def analyze_learning_style(quiz_results, lesson_completion_times):
    """
    Analyze a learner's style based on their quiz performance and learning patterns.
    Returns insights about learning preferences.
    """
    if not quiz_results or not lesson_completion_times:
        return {
            "style": "balanced",
            "insights": ["Not enough data for analysis"]
        }
    
    # Calculate average quiz performance
    avg_score = sum([r.get('score', 0) for r in quiz_results]) / len(quiz_results)
    
    # Analyze timing patterns
    avg_time = sum(lesson_completion_times) / len(lesson_completion_times) if lesson_completion_times else 0
    
    # Determine learning style
    if avg_score >= 80:
        if avg_time < 30:  # Fast learning
            style = "quick_learner"
            insights = [
                "You have excellent comprehension skills!",
                "Consider challenging yourself with advanced courses.",
                "You absorb information quickly and effectively."
            ]
        else:
            style = "thorough_learner"
            insights = [
                "You take your time to fully understand concepts.",
                "You have strong attention to detail.",
                "Keep up the methodical approach!"
            ]
    else:
        style = "developing_learner"
        insights = [
            "Consider reviewing previous lessons to strengthen your foundation.",
            "Take your time with each concept.",
            "Practice regularly to improve your performance."
        ]
    
    return {
        "style": style,
        "average_score": round(avg_score, 2),
        "average_time_per_lesson": round(avg_time, 2),
        "insights": insights
    }

def generate_personalized_path(user_profile, completed_courses, all_courses):
    """
    Generate a personalized learning path based on user profile and past performance.
    Uses collaborative filtering and content-based recommendations.
    """
    if not all_courses:
        return []
    
    # Extract user interests
    user_interests = user_profile.get('interests', [])
    skill_level = user_profile.get('skill_level', 'beginner')
    
    # Content-based filtering
    recommended_courses = []
    
    for course in all_courses:
        # Skip already completed courses
        if course.id in [c.id for c in completed_courses]:
            continue
        
        score = 0
        
        # Interest matching
        category = course.category.lower()
        for interest in user_interests:
            if interest.lower() in category or category in interest.lower():
                score += 3
        
        # Skill level matching
        if course.difficulty_level.lower() == skill_level.lower():
            score += 2
        elif course.difficulty_level.lower() == 'intermediate' and skill_level.lower() == 'beginner':
            score += 1
        
        # Popularity bonus
        score += min(len(course.enrollments) / 10, 1)
        
        if score > 0:
            recommended_courses.append({
                'course': course,
                'score': score,
                'reason': f"Matches your {', '.join(user_interests)} interests" if user_interests else "Recommended based on your skill level"
            })
    
    # Sort by score and return top recommendations
    recommended_courses.sort(key=lambda x: x['score'], reverse=True)
    
    return recommended_courses[:5]

def get_learning_insights(user_id, courses, quiz_attempts, lesson_progress):
    """
    Generate AI-powered insights about the learner's progress and performance.
    """
    insights = []
    
    # Calculate completion rate
    total_lessons = 0
    completed_lessons = len(lesson_progress)
    
    for course in courses:
        total_lessons += len(course.lessons)
    
    completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Performance insights
    if quiz_attempts:
        avg_score = sum([attempt.score for attempt in quiz_attempts]) / len(quiz_attempts)
        
        if avg_score >= 80:
            insights.append("🌟 Excellent performance! You're mastering the concepts.")
        elif avg_score >= 70:
            insights.append("👍 Good progress! Keep practicing to improve further.")
        else:
            insights.append("💪 Focus on reviewing the material and taking notes.")
    
    # Learning streak
    insights.append(f"📚 You've completed {completed_lessons} lessons so far!")
    
    # Recommendations
    if completion_rate < 30:
        insights.append("🎯 Consider focusing on one course at a time for better results.")
    elif completion_rate >= 80:
        insights.append("⭐ Outstanding commitment! You're making great progress.")
    
    return insights

def smart_content_generator(topic, difficulty_level="beginner"):
    """
    Generate smart, AI-enhanced content for a given topic.
    Uses templates enhanced with AI concepts.
    """
    templates = {
        "beginner": f"""
# Introduction to {topic}

Welcome to learning {topic}! This is a fundamental concept that you'll use throughout your learning journey.

## What is {topic}?
{topic} is an essential concept that forms the foundation of this subject. Understanding {topic} will help you grasp more advanced topics later.

## Key Concepts
1. Understanding the basics of {topic}
2. Common use cases
3. Best practices

## Learning Objectives
By the end of this lesson, you will:
- Understand what {topic} is
- Know when and why to use {topic}
- Be able to apply {topic} in simple scenarios
""",
        "intermediate": f"""
# Deep Dive into {topic}

This intermediate course will expand your understanding of {topic} and its applications.

## Advanced Concepts
Building on your basic knowledge, we'll explore:
- Advanced techniques for using {topic}
- Common pitfalls and how to avoid them
- Best practices and design patterns

## Real-World Applications
{topic} is used in many production systems. We'll examine real-world examples and case studies.

## Practice Exercises
Hands-on exercises will help you master {topic} through practical application.
""",
        "advanced": f"""
# Mastering {topic}

This advanced course is designed for experienced practitioners ready to push boundaries.

## Advanced Techniques
- Deep dive into {topic} internals
- Optimization strategies
- Advanced patterns and architectures

## Expert Insights
Learn from real-world case studies and expert best practices.

## Challenge Projects
Complex, real-world projects to demonstrate mastery of {topic}.
"""
    }
    
    return templates.get(difficulty_level, templates["beginner"])

def analyze_quiz_performance(quiz_attempts):
    """
    AI-powered analysis of quiz performance to identify strengths and weaknesses.
    """
    if not quiz_attempts:
        return {
            "strengths": [],
            "weaknesses": [],
            "recommendations": ["Start taking quizzes to get performance insights"]
        }
    
    # Analyze scores
    scores = [attempt.score for attempt in quiz_attempts]
    avg_score = sum(scores) / len(scores)
    
    strengths = []
    weaknesses = []
    recommendations = []
    
    if avg_score >= 80:
        strengths.append("Strong grasp of concepts")
        recommendations.append("Consider moving to more advanced courses")
    elif avg_score >= 70:
        strengths.append("Good understanding, room for improvement")
        recommendations.append("Review challenging topics and retake quizzes")
    else:
        weaknesses.append("Need more practice with core concepts")
        recommendations.append("Focus on understanding fundamentals before advancing")
    
    # Performance trend
    if len(scores) >= 3:
        recent_avg = sum(scores[-3:]) / 3
        earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else recent_avg
        
        if recent_avg > earlier_avg:
            strengths.append("Showing improvement over time")
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "average_score": round(avg_score, 2)
    }
