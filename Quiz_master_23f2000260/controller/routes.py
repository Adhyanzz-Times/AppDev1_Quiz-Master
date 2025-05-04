from app import app
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from controller.database import db
from controller.models import *
from datetime import datetime
from datetime import timedelta
import os
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        admin_email = 'admin@gmail.com'
        admin_password = '1234567890'

        if email == admin_email and password == admin_password:
            session['user_email'] = admin_email
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        if not email or not password:
            flash('Please enter email and password', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found', 'danger')
            return render_template('login.html')

        if user.password != password:
            flash('Password incorrect', 'danger')
            return render_template('login.html')

        if user.flag:
            flash('User is deactivated', 'warning')
            return render_template('login.html')

        session['user_email'] = user.email
        session['role'] = user.role if hasattr(user, 'role') else "user"
        
        return redirect(url_for('admin_dashboard') if session['role'] == "admin" else url_for('user_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification', "")
        dob = request.form.get('dob', "")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered. Try logging in!", "danger")
            return render_template('register.html')

        user = User(email=email, password=password, name=full_name, qualification=qualification, dob=dob, role='user')

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    subjects = Subject.query.all()
    chapters_count = Chapter.query.count()
    quizzes_count = Quiz.query.count()
    users_count = User.query.count()
    
    if request.method == 'POST':
        action = request.form.get('action')
        subject_id = request.form.get('subject_id')
        subject_name = request.form.get('subject_name')
        subject_description = request.form.get('subject_description')
        search_query = request.form.get('search_query')  # Get the search query

        if action == 'add_subject':
            if subject_name and subject_description:
                new_subject = Subject(name=subject_name, description=subject_description)
                db.session.add(new_subject)
                db.session.commit()
        elif action == 'edit_subject' and subject_id:
            subject = Subject.query.get(subject_id)
            if subject:
                subject.name = subject_name
                subject.description = subject_description
                db.session.commit()
        elif action == 'delete_subject' and subject_id:
            subject = Subject.query.get(subject_id)
            if subject:
                db.session.delete(subject)
                db.session.commit()
        elif action == 'search_all' and search_query:  # Handle search action
            search_results = []
            
            # Search Users
            users = User.query.filter(User.name.like(f'%{search_query}%') | User.email.like(f'%{search_query}%')).all()
            for user in users:
                search_results.append({'type': 'user', 'name': user.name, 'email': user.email})
            
            # Search Quizzes
            quizzes = Quiz.query.filter(Quiz.name.like(f'%{search_query}%')).all()
            for quiz in quizzes:
                chapter = Chapter.query.get(quiz.chapter_id)
                search_results.append({'type': 'quiz', 'name': quiz.name, 'chapter_name': chapter.name})
            
            # Search Chapters
            chapters = Chapter.query.filter(Chapter.name.like(f'%{search_query}%')).all()
            for chapter in chapters:
                subject = Subject.query.get(chapter.subject_id)
                search_results.append({'type': 'chapter', 'name': chapter.name, 'subject_name': subject.name})
            
            # Search Subjects
            subjects_found = Subject.query.filter(Subject.name.like(f'%{search_query}%')).all()
            for subject in subjects_found:
                search_results.append({'type': 'subject', 'name': subject.name})
            
            return render_template('admin_dashboard.html', 
                                   subjects=subjects, 
                                   chapters_count=chapters_count,
                                   quizzes_count=quizzes_count,
                                   users_count=users_count,
                                   search_results=search_results)  # Pass search results to template

        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', 
                           subjects=subjects, 
                           chapters_count=chapters_count,
                           quizzes_count=quizzes_count,
                           users_count=users_count)



@app.route('/dashboard', methods=['GET', 'POST'])
def user_dashboard():
    subjects = Subject.query.all()
    chapters = []
    available_quizzes = []
    past_quiz_results = []

    selected_subject_id = request.form.get('subject_id')
    selected_chapter_id = request.form.get('chapter_id')

    if selected_subject_id:
        chapters = Chapter.query.filter_by(subject_id=selected_subject_id).all()
        
        if selected_chapter_id:
            available_quizzes = Quiz.query.filter_by(chapter_id=selected_chapter_id).all()
        else:
            chapter_ids = [chapter.id for chapter in chapters]
            available_quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
    else:
        chapters = Chapter.query.all()


    if request.method == 'POST' and 'start_quiz' in request.form:
        quiz_id = request.form.get('quiz_id')
        if quiz_id:
            return redirect(url_for('start_quiz', quiz_id=quiz_id))
        else:
            flash('Please select a quiz to start.', 'error')

    return render_template('user_dashboard.html', 
                           subjects=subjects, 
                           chapters=chapters, 
                           available_quizzes=available_quizzes,
                           selected_subject_id=selected_subject_id,
                           selected_chapter_id=selected_chapter_id,
                           past_quiz_results=past_quiz_results)


@app.route('/view_scores')
def view_scores():
 
    user_email = session['user_email']
    user = User.query.filter_by(email=user_email).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('login'))

    
    scores = (
        db.session.query(
            Subject.name.label("subject_name"),
            Chapter.name.label("chapter_name"),
            Quiz.name.label("quiz_name"),
            Score.total_scored,
        )
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Score, Score.quiz_id == Quiz.id)
        .filter(Score.user_id == user.id)
        .all()
    )

    if not scores:
        flash("No quiz scores available.", "info")
        return render_template('view_scores.html', scores=None, graph_url=None)

    
    quiz_names = []
    total_scores = []
    for score in scores:
        quiz_names.append(f"{score.subject_name} - {score.quiz_name}")  
        total_scores.append(score.total_scored)

    
    img = io.BytesIO()
    plt.figure(figsize=(8, 5))
    plt.bar(quiz_names, total_scores, color='skyblue', alpha=0.8)

    plt.xlabel("Quizzes")
    plt.ylabel("Total Score")
    plt.title(f"Quiz Performance of {user.email}")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y')

    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template('view_scores.html', scores=scores, graph_url=graph_url)


@app.route('/chapter_management', methods=['GET', 'POST'])
def chapter_management():
    subjects = Subject.query.all()
    selected_subject_id = request.form.get('subject_id')
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action:
            chapter_id = request.form.get('chapter_id')
            chapter_name = request.form.get('chapter_name')
            chapter_description = request.form.get('chapter_description')
            
            if action == 'add_chapter' and selected_subject_id:
                new_chapter = Chapter(name=chapter_name, description=chapter_description, subject_id=selected_subject_id)
                db.session.add(new_chapter)
            elif action == 'edit_chapter' and chapter_id:
                chapter = Chapter.query.get(chapter_id)
                if chapter:
                    chapter.name = chapter_name
                    chapter.description = chapter_description
            elif action == 'delete_chapter' and chapter_id:
                chapter = Chapter.query.get(chapter_id)
                if chapter:
                    db.session.delete(chapter)
            
            db.session.commit()
            return redirect(url_for('chapter_management', subject_id=selected_subject_id))
    
    if selected_subject_id:
        chapters = Chapter.query.filter_by(subject_id=selected_subject_id).all()
    else:
        chapters = []
    
    return render_template('chapter_management.html', 
                           subjects=subjects, 
                           chapters=chapters, 
                           selected_subject_id=selected_subject_id)


@app.route('/quiz_management', methods=['GET', 'POST'])
def quiz_management():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_quiz':
            quiz_name = request.form.get('quiz_name')  
            chapter_id = request.form.get('chapter_id')
            quiz_date = request.form.get('quiz_date')
            quiz_duration = request.form.get('quiz_duration')
            quiz_remarks = request.form.get('quiz_remarks')

            
            if not all([quiz_name, chapter_id, quiz_date, quiz_duration, quiz_remarks]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('quiz_management'))

            try:
                new_quiz = Quiz(
                    name=quiz_name,  
                    chapter_id=chapter_id,
                    date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d').date(),
                    time_duration=quiz_duration,
                    remarks=quiz_remarks
                )
                db.session.add(new_quiz)
                db.session.commit()
                flash('Quiz created successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating quiz: {str(e)}', 'error')

    return render_template('quiz_management.html', subjects=subjects, chapters=chapters, quizzes=quizzes)



@app.route('/question_management', methods=['GET', 'POST'])
def question_management():
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    questions = Question.query.all()  

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_question':
            quiz_name = request.form.get('quiz_name')
            question_statement = request.form.get('question_statement')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_option = request.form.get('correct_option')

            
            quiz = Quiz.query.filter_by(name=quiz_name).first()
            if quiz:
                quiz_id = quiz.id
            else:
                flash('Quiz not found', 'error')
                return redirect(url_for('question_management'))

            if not all([quiz_id, question_statement, option1, option2, option3, option4, correct_option]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('question_management'))

            try:
                new_question = Question(
                    quiz_id=quiz_id,
                    question_statement=question_statement,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    correct_option=correct_option
                )
                db.session.add(new_question)
                db.session.commit()
                flash('Question added successfully!', 'success')
                return redirect(url_for('question_management'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding question: {str(e)}', 'error')
                return redirect(url_for('question_management'))

        elif action == 'delete_question':
            question_id = request.form.get('question_id')
            if not question_id:
                flash('Invalid question ID', 'error')
                return redirect(url_for('question_management'))

            try:
                question_to_delete = Question.query.get(question_id)
                if question_to_delete:
                    db.session.delete(question_to_delete)
                    db.session.commit()
                    flash('Question deleted successfully!', 'success')
                else:
                    flash('Question not found', 'error')
                return redirect(url_for('question_management'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error deleting question: {str(e)}', 'error')
                return redirect(url_for('question_management'))

    return render_template('question_management.html', quizzes=quizzes, subjects=subjects, questions=questions)


from datetime import datetime, timedelta

@app.route('/start_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer is not None and int(user_answer) == int(question.correct_option):
                score += 1

        total_questions = len(questions)
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        
        user_email = session.get('user_email')
        if user_email:
            
            user = User.query.filter_by(email=user_email).first()
            if user:
                
                new_score = Score(
                    quiz_id=quiz_id,
                    user_id=user.id,  
                    time_stamp_of_attempt=datetime.utcnow(),
                    total_scored=score
                )
                db.session.add(new_score)
                db.session.commit()
                flash(f'Quiz completed! Your score: {score}/{total_questions} ({percentage:.2f}%)', 'success')
            else:
                flash('User not found', 'error')
        else:
            flash('User not logged in', 'error')

        return redirect(url_for('user_dashboard'))

    
    session['quiz_start_time'] = datetime.utcnow().isoformat()

    return render_template('start_quiz.html', quiz=quiz, questions=questions)

@app.route('/edit_delete_quiz', methods=['GET', 'POST'])
def edit_delete_quiz():
    quizzes = Quiz.query.all()
    selected_quiz = None

    
    quiz_id = request.args.get('quiz_id')
    if quiz_id:
        selected_quiz = Quiz.query.get(quiz_id)

    if request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        action = request.form.get('action')

        if quiz_id:
            selected_quiz = Quiz.query.get(quiz_id)

        if action and selected_quiz:
            try:
                if action == 'edit_quiz':
                   
                    quiz_name = request.form.get('quiz_name')
                    quiz_description = request.form.get('quiz_description')
                    
                    if quiz_name and quiz_description:
                        selected_quiz.name = quiz_name
                        selected_quiz.description = quiz_description
                        db.session.commit()
                        flash('Quiz updated successfully!', 'success')
                    else:
                        flash('Please fill in all fields.', 'warning')
                elif action == 'delete_quiz':
                    db.session.delete(selected_quiz)
                    db.session.commit()
                    flash('Quiz deleted successfully!', 'danger')
                    selected_quiz = None  
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", 'danger')

        return redirect(url_for('edit_delete_quiz'))

    return render_template('edit_delete_quiz.html', quizzes=quizzes, selected_quiz=selected_quiz)

@app.route('/edit_delete_question', methods=['GET', 'POST'])
def edit_delete_question():
    subjects = Subject.query.all()
    selected_subject_id = request.form.get('subject_id')
    selected_chapter_id = request.form.get('chapter_id')
    selected_quiz_id = request.form.get('quiz_id')

    chapters = []
    quizzes = []
    questions = []

    if selected_subject_id:
        chapters = Chapter.query.filter_by(subject_id=selected_subject_id).all()

    if selected_chapter_id:
        quizzes = Quiz.query.filter_by(chapter_id=selected_chapter_id).all()

    if selected_quiz_id:
        questions = Question.query.filter_by(quiz_id=selected_quiz_id).all()

    if request.method == 'POST':
        action = request.form.get('action')
        question_id = request.form.get('question_id')

        if action == 'edit_question' and question_id:
            question = Question.query.get(question_id)
            if question:
                question.question_statement = request.form.get('question_text')
                question.option1 = request.form.get('option1')
                question.option2 = request.form.get('option2')
                question.option3 = request.form.get('option3')
                question.option4 = request.form.get('option4')
                question.correct_option = int(request.form.get('question_answer'))
                db.session.commit()
                flash('Question updated successfully', 'success')
            else:
                flash('Question not found', 'error')

        elif action == 'delete_question' and question_id:
            question = Question.query.get(question_id)
            if question:
                db.session.delete(question)
                db.session.commit()
                flash('Question deleted successfully', 'success')
            else:
                flash('Question not found', 'error')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('edit_delete_question.html', subjects=subjects, chapters=chapters, 
                                   quizzes=quizzes, questions=questions, selected_subject_id=selected_subject_id, 
                                   selected_chapter_id=selected_chapter_id, selected_quiz_id=selected_quiz_id)

    return render_template('edit_delete_question.html', subjects=subjects, chapters=chapters, 
                           quizzes=quizzes, questions=questions, selected_subject_id=selected_subject_id, 
                           selected_chapter_id=selected_chapter_id, selected_quiz_id=selected_quiz_id)



if __name__ == '__main__':
    app.run(debug=True)
