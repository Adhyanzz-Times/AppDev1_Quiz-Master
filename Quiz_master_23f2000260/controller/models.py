from controller.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    flag = db.Column(db.Boolean, default=False, nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True, cascade="all, delete")



class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)  
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.String(10), nullable=False)
    time_duration = db.Column(db.String(5), nullable=False)
    remarks = db.Column(db.Text, nullable=True)  

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=True) 
    question_statement = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    time_stamp_of_attempt = db.Column(db.String(20), nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
