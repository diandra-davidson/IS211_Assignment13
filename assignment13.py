#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Flask application using sqlite3 database"""


import sqlite3 as lite
import sys
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)
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


@app.route('/',  methods=['GET', 'POST'])
def home_pg():
    return render_template('login.html')


@app.route('/login',  methods=['GET', 'POST'])
def auth():
    username = request.form['username']
    password = request.form['password']


    return redirect('/dashboard')


if __name__ == '__main__':
    app.run()
