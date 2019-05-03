#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Flask application using sqlite3 database"""


import sqlite3 as lite
import re
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, current_app, g, flash, session)
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')
student_roster = []
quiz_roster = []


def get_db():
    if 'db' not in g:
        g.db = lite.connect('hw13.db')
        g.db.row_factory = lite.Row

    return g.db


@app.route('/',  methods=['GET'])
def home_pg():
    if 'logged_in' in session:
        return redirect('/dashboard')
    else:
        return render_template('auth/login.html')


@app.route('/dashboard',  methods=['GET'])
def dashboard():
    if 'logged_in' in session:
        return render_template('cms/dashboard.html',
                               student_roster=student_roster,
                               quiz_roster=quiz_roster)
    else:
        return redirect('/')


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        database = get_db()
        user = database.execute(
            'SELECT * FROM teachers WHERE username = ?',
            (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['logged_in'] = True
            session['user_id'] = user['teacher_id']

            for row in database.execute('SELECT * FROM students'):
                if row not in student_roster:
                    student_roster.append((row))

            for row in database.execute('SELECT * FROM quizzes'):
                if row not in quiz_roster:
                    quiz_roster.append((row))

            return redirect('/dashboard')

        flash(error)
        return render_template('auth/login.html')

    if request.method == 'GET':
        return redirect('/dashboard')


@app.route('/register',  methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        database = get_db()

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif database.execute(
                'SELECT teacher_id FROM teachers WHERE username = ?',
                (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            database.execute(
                'INSERT INTO teachers (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            database.commit()

        return redirect('/dashboard')

    elif request.method == 'GET':
        return render_template('auth/register.html')


@app.route('/student/add',  methods=['GET', 'POST'])
def addstudent():
    if 'logged_in' in session:
        if request.method == 'GET':
            return render_template('cms/add_student.html')
        elif request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            database = get_db()
            error = None

            if not firstname:
                error = 'First name is required.'
            elif not lastname:
                error = 'Last name is required.'

            if re.search(r'[!@#$%^&*(),.?":{}|<>]', firstname):
                error = "Invalid characters used. " \
                        "Please do not include special characters."
            elif re.search(r'[!@#$%^&*(),.?":{}|<>]', lastname):
                error = "Invalid characters used. " \
                        "Please do not include special characters."

            if error is None:
                database.execute(
                    'INSERT INTO students (first_name, last_name) '
                    'VALUES (?, ?)', (firstname, lastname))
                database.commit()

                for row in database.execute('SELECT * FROM students '
                                            'WHERE first_name=? AND '
                                            'last_name=?;',
                                            (firstname, lastname)):
                    student_roster.append((row))
                return redirect('/dashboard')

        flash(error)
        return render_template('cms/add_student.html')
    else:
        return redirect('/')


@app.route('/quiz/add',  methods=['GET', 'POST'])
def addquiz():
    if 'logged_in' in session:
        if request.method == 'GET':
            return render_template('cms/add_quiz.html')
        elif request.method == 'POST':
            subject = request.form['subject']
            num_of_questions = request.form['num_of_questions']
            quiz_date = request.form['date']
            database = get_db()
            error = None

            if not subject:
                error = 'Subject is required.'
            elif not num_of_questions:
                error = 'Number of questions is required.'
            elif not quiz_date:
                error = 'Quiz date is required.'

            if re.search(r'[!@#$%^&*(),.?":{}|<>]', subject):
                error = "Invalid characters used in Subject. " \
                        "Please do not include special characters."

            if error is None:
                database.execute(
                    'INSERT INTO quizzes (subject, num_of_questions, date) '
                    'VALUES (?, ?, ?)', (subject, num_of_questions, quiz_date))
                database.commit()

                for row in database.execute('SELECT * FROM quizzes '
                                            'WHERE subject=? AND '
                                            'num_of_questions=? AND '
                                            'date=?;',
                                            (subject, num_of_questions,
                                             quiz_date)):
                    quiz_roster.append((row))
                return redirect('/dashboard')

        flash(error)
        return render_template('cms/add_quiz.html')
    else:
        return redirect('/')


@app.route('/student/<path:student_id>', methods=['GET'])
def viewstudent(student_id):
    if 'logged_in' in session:
        student_data = []
        student_name = []
        id = student_id
        database = get_db()

        for row in database.execute('SELECT first_name, last_name '
                                    'FROM students '
                                    'WHERE student_id=?;', id):
            if row not in student_name:
                student_name.append((row))

        for row in database.execute('SELECT quizzes.quiz_id,'
                                    'quizzes.subject, '
                                    'quizzes.num_of_questions, '
                                    'quizzes.date, '
                                    'scores.score FROM quizzes '
                                    'JOIN scores using (quiz_id) '
                                    'WHERE student_id=?;', id):
            if row not in student_data:
                student_data.append((row))

        return render_template('cms/student.html',
                               student_id=student_id,
                               student_data=student_data,
                               student_name=student_name)


@app.route('/results/add', methods=['GET', 'POST'])
def add_score():
    if 'logged_in' in session and request.method == 'GET':
        student_list = []
        quiz_list = []
        database = get_db()

        for row in database.execute('SELECT * FROM students;'):
            if row not in student_list:
                student_list.append((row))

        for row in database.execute('SELECT quiz_id, subject FROM quizzes;'):
            if row not in quiz_list:
                quiz_list.append((row))

        return render_template('cms/add_score.html',
                               student_list=student_list,
                               quiz_list=quiz_list)

    elif 'logged_in' in session and request.method == 'POST':
        student = request.form['studentList']
        quiz = request.form['quizList']
        score = request.form['score']
        database = get_db()
        message = None

        duplicates = database.execute('SELECT * FROM scores WHERE student_id=? AND '
                            'quiz_id=?;', (student, quiz))

        if duplicates.fetchone() is None:
            database.execute('INSERT INTO scores(student_id, quiz_id, score) '
                             'VALUES(?, ?, ?);', (student, quiz, score))
            database.commit()
            message = "Quiz added successfully!"
        else:
            message = "Duplicate quiz for this student found."

        flash(message)

        return redirect('/results/add')

    else:
        return redirect('/')


if __name__ == '__main__':
    app.run()
