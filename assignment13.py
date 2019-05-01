#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Flask application using sqlite3 database"""


#export FLASK_ENV=development

import sqlite3 as lite
import sys
import re
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, current_app, g, flash, session)
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')
student_roster = []
quiz_roster = []

student = (('John', 'Smith'))
quiz = (('Python Basics', 5, 'February, 5th, 2015'))
score = ((1, 1, 85))


#try:
#    con = lite.connect('hw13.db')
#    cur = con.cursor()
#
#    cur.execute("INSERT INTO students(first_name, last_name) "
#                "VALUES(?, ?)", student)
#    cur.execute("INSERT INTO quizzes(subject, num_of_questions, date) "
#                "VALUES(?, ?, ?)", quiz)
#    cur.execute("INSERT INTO scores(student_id, quiz_id, score) "
#                "VALUES(?, ?, ?)", score)
#
#    con.commit()
#
#except lite.Error, e:
#    if con:
#        con.rollback()
#    print "Error {}".format(e.args[0])
#    sys.exit(1)
#
#finally:
#    if con:
#        con.close()


def get_db():
    if 'db' not in g:
        g.db = lite.connect('hw13.db')
        g.db.row_factory = lite.Row

    return g.db


@app.route('/',  methods=['GET'])
def home_pg():
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
                student_roster.append((row))

            for row in database.execute('SELECT * FROM quizzes'):
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


if __name__ == '__main__':
    app.run()
