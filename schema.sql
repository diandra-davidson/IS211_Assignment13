DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS quizzes;
DROP TABLE IF EXISTS scores;

CREATE TABLE students (
  student_id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);

CREATE TABLE quizzes (
  quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject TEXT NOT NULL,
  num_of_questions INTEGER NOT NULL,
  date TEXT NOT NULL
);

CREATE TABLE scores (
  student_id INTEGER NOT NULL,
  quiz_id INTEGER NOT NULL,
  score INTEGER NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id)
);