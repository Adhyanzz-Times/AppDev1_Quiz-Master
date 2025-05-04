# 🎓 Quiz Master - Modular Quiz Management System

![QuizMaster Banner](https://img.shields.io/badge/Flask-App-blue?style=for-the-badge&logo=flask)

## 📖 Overview

**QuizMaster** is a structured and user-friendly educational assessment app developed using **Flask**. It allows:

---

## 🚀 Key Features

### 🛠 Admin Panel
- Full **CRUD operations**:
  - Subjects
  - Chapters
  - Quizzes
  - Questions
- Dynamic dashboard with:
  - Quiz statistics
- Modal-based entity creation (without page reloads)

### 👨‍🎓 User Portal
- Secure **Registration/Login**
- Explore subjects and quizzes
- Attempt quizzes with auto-scoring
- View **historical performance** and quiz attempts

🌐 The app ensures real-time feedback and performance insights, aiding both teaching and learning.

---

## 🧰 Tech Stack

| Layer           | Technologies Used |
|----------------|-------------------|
| 🖥️ Frontend    | HTML5, CSS3, Bootstrap, Jinja2 |
| ⚙️ Backend     | Flask, Flask-SQLAlchemy, Werkzeug |
| 💾 Database    | SQLite |
| 🛡️ Security    | Password Hashing & Role-Based Access |
| 🔐 Session     | Flask Sessions for Auth & State |

---

## 🧬 Database Schema Overview

- **User**
  - `id`, `username`, `password`, `is_admin`, `scores[]`
- **Subject**
  - `id`, `name`, `description`, `chapters[]`
- **Chapter**
  - `id`, `name`, `subject_id`, `quizzes[]`
- **Quiz**
  - `id`, `title`, `date_of_quiz`, `time_duration`, `chapter_id`, `questions[]`, `scores[]`
- **Question**
  - `id`, `question_statement`, `option1-4`, `correct_option`, `quiz_id`
- **Score**
  - `id`, `user_id`, `quiz_id`, `score`, `total_questions`, `timestamp`

> Relationships use SQLAlchemy backrefs with cascade deletes for integrity.

---

## 🖥️ System Flow

```plaintext
Admin:
  Create Subject → Add Chapter → Add Quiz → Add Questions
User:
  Browse → Attempt Quiz → View Results & Past Scores
```


## Development Server

```plaintext
- python app.py
- Default runs at http://127.0.0.1:5000
```


Made with ❤️ using Flask (Python).
