import json
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import DepartmentHead, Parent, Student, User
from app.models import NewsAndEvents, Semester, Session
from course.models import Course, CourseAllocation, Program
from coursemanagement.models import CourseOffer, CourseSetting
from payments.models import Invoice
from quiz.models import Choice, MCQuestion, Progress, Quiz, Sitting
from result.models import Result, TakenCourse


DEMO_PASSWORD = "Demo@12345"


class Command(BaseCommand):
    help = "Create a connected demo dataset for local development and portfolio review."

    @transaction.atomic
    def handle(self, *args, **options):
        session, _ = Session.objects.update_or_create(
            session="2025/2026",
            defaults={
                "is_current_session": True,
                "next_session_begins": date(2026, 9, 1),
            },
        )
        Session.objects.exclude(pk=session.pk).update(is_current_session=False)

        semester, _ = Semester.objects.update_or_create(
            semester="First",
            session=session,
            defaults={
                "is_current_semester": True,
                "next_semester_begins": date(2026, 8, 15),
            },
        )
        Semester.objects.exclude(pk=semester.pk).update(is_current_semester=False)

        programs = self.create_programs()
        courses = self.create_courses(programs)
        lecturers = self.create_lecturers()
        students = self.create_students(programs)
        self.create_parents(students)
        self.create_department_heads(lecturers, programs)
        self.create_allocations(lecturers, courses, session)
        self.create_academic_records(students, courses, session)
        self.create_quizzes(students, courses)
        self.create_news()
        self.create_invoices(students)
        self.create_course_settings()

        self.stdout.write(self.style.SUCCESS("Demo university data is ready."))
        self.stdout.write("Shared demo password: Demo@12345")
        self.stdout.write("Lecturer: lecturer.amina")
        self.stdout.write("Student: student.ali")
        self.stdout.write("Parent: parent.ali")

    def create_programs(self):
        rows = [
            (
                "Computer Science",
                "Software engineering, artificial intelligence, databases, and computing systems.",
            ),
            (
                "Business Administration",
                "Management, finance, entrepreneurship, marketing, and organizational leadership.",
            ),
            (
                "Electrical Engineering",
                "Electronics, embedded systems, communications, control, and power engineering.",
            ),
        ]
        return {
            title: Program.objects.update_or_create(
                title=title, defaults={"summary": summary}
            )[0]
            for title, summary in rows
        }

    def create_courses(self, programs):
        rows = [
            ("Programming Fundamentals", "CS101", 4, "Computer Science", 1, "First", False),
            ("Database Systems", "CS220", 3, "Computer Science", 2, "First", False),
            ("Artificial Intelligence", "CS340", 3, "Computer Science", 3, "First", False),
            ("Web Engineering", "CS315", 3, "Computer Science", 3, "First", True),
            ("Principles of Management", "BBA101", 3, "Business Administration", 1, "First", False),
            ("Financial Accounting", "BBA210", 3, "Business Administration", 2, "First", False),
            ("Digital Logic Design", "EE120", 4, "Electrical Engineering", 1, "First", False),
            ("Signals and Systems", "EE230", 3, "Electrical Engineering", 2, "First", False),
        ]
        courses = {}
        for title, code, credit, program, year, semester, elective in rows:
            course, _ = Course.objects.update_or_create(
                code=code,
                defaults={
                    "title": title,
                    "credit": credit,
                    "summary": f"Core concepts and applied coursework in {title.lower()}.",
                    "program": programs[program],
                    "level": "Bachloar",
                    "year": year,
                    "semester": semester,
                    "is_elective": elective,
                },
            )
            courses[code] = course
        return courses

    def create_user(self, username, first_name, last_name, email, **roles):
        user, _ = User.objects.get_or_create(username=username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = roles.pop("phone", "+92 300 0000000")
        user.address = roles.pop("address", "Islamabad, Pakistan")
        for field, value in roles.items():
            setattr(user, field, value)
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user

    def create_lecturers(self):
        rows = [
            ("lecturer.amina", "Amina", "Khan", "amina.khan@university.test"),
            ("lecturer.hamza", "Hamza", "Ahmed", "hamza.ahmed@university.test"),
            ("lecturer.sara", "Sara", "Malik", "sara.malik@university.test"),
        ]
        return [
            self.create_user(*row, is_lecturer=True, is_staff=False) for row in rows
        ]

    def create_students(self, programs):
        rows = [
            ("student.ali", "Ali", "Raza", "ali.raza@student.test", "Computer Science"),
            ("student.fatima", "Fatima", "Noor", "fatima.noor@student.test", "Computer Science"),
            ("student.usman", "Usman", "Tariq", "usman.tariq@student.test", "Business Administration"),
            ("student.zoya", "Zoya", "Saeed", "zoya.saeed@student.test", "Electrical Engineering"),
            ("student.bilal", "Bilal", "Hassan", "bilal.hassan@student.test", "Computer Science"),
            ("student.hira", "Hira", "Iqbal", "hira.iqbal@student.test", "Business Administration"),
        ]
        students = {}
        for username, first, last, email, program_name in rows:
            user = self.create_user(
                username, first, last, email, is_student=True
            )
            student, _ = Student.objects.update_or_create(
                student=user,
                defaults={
                    "level": "Bachloar",
                    "department": programs[program_name],
                },
            )
            students[username] = student
        return students

    def create_parents(self, students):
        rows = [
            ("parent.ali", "Nadeem", "Raza", "student.ali", "Father"),
            ("parent.fatima", "Samina", "Noor", "student.fatima", "Mother"),
        ]
        for username, first, last, student_username, relationship in rows:
            user = self.create_user(
                username,
                first,
                last,
                f"{username}@family.test",
                is_parent=True,
            )
            Parent.objects.update_or_create(
                user=user,
                defaults={
                    "student": students[student_username],
                    "first_name": first,
                    "last_name": last,
                    "phone": user.phone,
                    "email": user.email,
                    "relation_ship": relationship,
                },
            )

    def create_department_heads(self, lecturers, programs):
        assignments = [
            (lecturers[0], programs["Computer Science"]),
            (lecturers[1], programs["Business Administration"]),
            (lecturers[2], programs["Electrical Engineering"]),
        ]
        for lecturer, program in assignments:
            lecturer.is_dep_head = True
            lecturer.save(update_fields=["is_dep_head"])
            DepartmentHead.objects.update_or_create(
                user=lecturer, defaults={"department": program}
            )

    def create_allocations(self, lecturers, courses, session):
        groups = [
            (lecturers[0], ["CS101", "CS220", "CS340"]),
            (lecturers[1], ["BBA101", "BBA210"]),
            (lecturers[2], ["EE120", "EE230", "CS315"]),
        ]
        for lecturer, codes in groups:
            allocation, _ = CourseAllocation.objects.get_or_create(
                lecturer=lecturer, session=session
            )
            allocation.courses.set([courses[code] for code in codes])

    def create_academic_records(self, students, courses, session):
        enrollment = {
            "student.ali": ["CS101", "CS220", "CS340", "CS315"],
            "student.fatima": ["CS101", "CS220", "CS340"],
            "student.usman": ["BBA101", "BBA210"],
            "student.zoya": ["EE120", "EE230"],
            "student.bilal": ["CS101", "CS220", "CS315"],
            "student.hira": ["BBA101", "BBA210"],
        }
        scores = [
            (17, 19, 8, 9, 38),
            (15, 17, 9, 8, 35),
            (18, 18, 8, 10, 40),
            (14, 16, 7, 9, 34),
        ]
        for student_index, (username, codes) in enumerate(enrollment.items()):
            student = students[username]
            totals = []
            for course_index, code in enumerate(codes):
                assignment, mid, quiz_score, attendance, final = scores[
                    (student_index + course_index) % len(scores)
                ]
                total = assignment + mid + quiz_score + attendance + final
                record = TakenCourse(student=student, course=courses[code])
                grade = record.get_grade(total)
                record.assignment = Decimal(assignment)
                record.mid_exam = Decimal(mid)
                record.quiz = Decimal(quiz_score)
                record.attendance = Decimal(attendance)
                record.final_exam = Decimal(final)
                record.total = Decimal(total)
                record.grade = grade
                record.comment = record.get_comment(grade)
                record.point = Decimal(str(record.get_point(grade)))
                TakenCourse.objects.update_or_create(
                    student=student,
                    course=courses[code],
                    defaults={
                        "assignment": record.assignment,
                        "mid_exam": record.mid_exam,
                        "quiz": record.quiz,
                        "attendance": record.attendance,
                        "final_exam": record.final_exam,
                        "total": record.total,
                        "grade": record.grade,
                        "comment": record.comment,
                        "point": record.point,
                    },
                )
                totals.append(total)
            gpa = round(min(4.0, sum(totals) / len(totals) / 25), 2)
            Result.objects.update_or_create(
                student=student,
                semester="First",
                level="Bachloar",
                defaults={
                    "gpa": gpa,
                    "cgpa": gpa,
                    "session": session.session,
                },
            )

    def create_quizzes(self, students, courses):
        quiz_specs = [
            (
                courses["CS101"],
                "Python Fundamentals",
                "Assess variables, data types, and control flow.",
                [
                    ("Which keyword defines a function in Python?", ["func", "def", "function", "method"], 1),
                    ("Which collection stores unique values?", ["List", "Tuple", "Set", "String"], 2),
                    ("What does len() return?", ["Type", "Length", "Value", "Index"], 1),
                ],
            ),
            (
                courses["CS220"],
                "Database Essentials",
                "Review relational modeling, SQL, and normalization.",
                [
                    ("Which SQL command reads rows?", ["SELECT", "UPDATE", "DROP", "ALTER"], 0),
                    ("A primary key must be:", ["Nullable", "Unique", "Repeated", "Optional"], 1),
                    ("Normalization primarily reduces:", ["Indexes", "Redundancy", "Tables", "Queries"], 1),
                ],
            ),
        ]
        quizzes = []
        for course, title, description, questions in quiz_specs:
            quiz, _ = Quiz.objects.update_or_create(
                title=title,
                defaults={
                    "course": course,
                    "description": description,
                    "category": "practice",
                    "random_order": False,
                    "answers_at_end": True,
                    "exam_paper": True,
                    "single_attempt": False,
                    "pass_mark": 50,
                    "draft": False,
                },
            )
            quizzes.append(quiz)
            for content, choices, correct_index in questions:
                question, _ = MCQuestion.objects.update_or_create(
                    content=content,
                    defaults={
                        "explanation": "Review the related course material for this concept.",
                        "choice_order": "none",
                    },
                )
                question.quiz.add(quiz)
                Choice.objects.filter(question=question).delete()
                for index, choice in enumerate(choices):
                    Choice.objects.create(
                        question=question,
                        choice=choice,
                        correct=index == correct_index,
                    )

        student_user = students["student.ali"].student
        Progress.objects.update_or_create(user=student_user, defaults={"score": "1,3,3"})
        first_quiz = quizzes[0]
        questions = list(first_quiz.get_questions())
        question_ids = [question.id for question in questions]
        order = ",".join(str(value) for value in question_ids)
        user_answers = {}
        for question in questions:
            correct_choice = question.choice_set.filter(correct=True).first()
            if correct_choice:
                user_answers[str(question.id)] = str(correct_choice.id)
        Sitting.objects.update_or_create(
            user=student_user,
            quiz=first_quiz,
            course=first_quiz.course,
            complete=True,
            defaults={
                "question_order": order,
                "question_list": "",
                "incorrect_questions": "",
                "current_score": len(question_ids),
                "user_answers": json.dumps(user_answers),
                "end": timezone.now(),
            },
        )

    def create_news(self):
        rows = [
            ("Fall Registration Opens", "Course registration is open through the student portal.", "News"),
            ("AI Research Showcase", "Student teams will present applied AI projects in the main auditorium.", "Event"),
            ("Midterm Examination Schedule", "The consolidated midterm schedule is now available.", "News"),
            ("Career Fair 2026", "Meet technology, finance, and engineering employers on campus.", "Event"),
            ("Library Hours Extended", "The central library will remain open until midnight during exams.", "News"),
            ("Inter-University Sports Week", "Registrations are open for football, cricket, and badminton.", "Event"),
        ]
        for title, summary, posted_as in rows:
            NewsAndEvents.objects.update_or_create(
                title=title,
                defaults={"summary": summary, "posted_as": posted_as},
            )

    def create_invoices(self, students):
        rows = [
            ("student.ali", 85000, 85000, True, "INV-2026-1001"),
            ("student.fatima", 85000, 45000, False, "INV-2026-1002"),
            ("student.usman", 72000, 72000, True, "INV-2026-1003"),
            ("student.zoya", 90000, 50000, False, "INV-2026-1004"),
        ]
        for username, total, amount, complete, code in rows:
            Invoice.objects.update_or_create(
                invoice_code=code,
                defaults={
                    "user": students[username].student,
                    "total": total,
                    "amount": amount,
                    "payment_complete": complete,
                },
            )

    def create_course_settings(self):
        setting = CourseSetting.objects.first()
        if setting is None:
            CourseSetting.objects.create(add_drop=True)
        else:
            setting.add_drop = True
            setting.save(update_fields=["add_drop"])

        for head in DepartmentHead.objects.select_related("user"):
            CourseOffer.objects.get_or_create(dep_head=head)
