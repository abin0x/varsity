# 🌟 University Management System

👤 **Name:** Mahmudul Hasan Abin  
📚 **Project Name:** University Management System
#  About

**Introducing the University Class Schedule, Notice, Assignment, Research Paper Submission, and Attendance System!**
The Online Library Management System is designed to help users and administrators manage a library efficiently. It allows users to borrow books, view their borrowing history, and manage their profiles, while administrators can manage the entire library inventory (books, categories, authors), issue and return books, and track user activities such as borrowed books, fines, and membership statuses. The system is built using Django Rest Framework (DRF) and follows a token-based authentication system.
Our platform streamlines university management with dedicated dashboards for **Teachers**, **Students**, and **Class Representatives (CRs)**. 

<p align="center"><img src="https://i.ibb.co.com/qMhcXzP/all-devices-black.png" alt="project-image"></p>

---

## 🚀 Features

- **Manage Schedules**: 📅 Students can view and manage their class schedules effortlessly.
- **View Assignments**: 📚 Easily access all assigned coursework and track due dates.
- **Submit Assignments**: 📤 Submit individual assignments directly through the platform.
- **Research Paper Tracking**: 📑 Keep track of submitted research papers and their statuses.
- **Notice Board**: 📣 View important notices and announcements relevant to all users.
- **Email Notifications**: 📧 All updates are sent via email and displayed on the home page for quick access.
- **Personalized Access**: 👥 Each user type (Students, Teachers, CRs) benefits from a tailored experience to ensure smooth academic operations.

---

## 💻 Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Django REST Framework

---

## 🌐 Live Demo

Experience the system live at [https://hstu.netlify.app/](https://hstu.netlify.app/).

---

## API Endpoints

- **Filter**: [`http://127.0.0.1:8000/api/courses?department=eee`](http://127.0.0.1:8000/api/courses?department=eee)
- **Teacher Login**: [`http://127.0.0.1:8000/api/users/login`](http://127.0.0.1:8000/api/users/login)
- **Individual Course Details**: [`http://127.0.0.1:8000/api/courses/4`](http://127.0.0.1:8000/api/courses/4)
- **Teacher Logout**: [`http://127.0.0.1:8000/api/users/logout`](http://127.0.0.1:8000/api/users/logout)
- **All Courses**: [`http://127.0.0.1:8000/api/courses`](http://127.0.0.1:8000/api/courses)
- **Teacher Registration**: [`http://127.0.0.1:8000/api/users/register`](http://127.0.0.1:8000/api/users/register)
- **Activate Account**: [`http://127.0.0.1:8000/api/users/activate/<uid64>/<token>/`](http://127.0.0.1:8000/api/users/activate/<uid64>/<token>/)
- **Service**: [`http://127.0.0.1:8000/api/services/`](http://127.0.0.1:8000/api/services/)
- **Contact Us**: [`http://127.0.0.1:8000/api/contact/`](http://127.0.0.1:8000/api/contact/)
- **Blog**: [`http://127.0.0.1:8000/api/posts/`](http://127.0.0.1:8000/api/posts/)
- **Blog Details**: [`http://127.0.0.1:8000/api/posts/13`](http://127.0.0.1:8000/api/posts/13)
- **All Teachers**: [`http://127.0.0.1:8000/api/users`](http://127.0.0.1:8000/api/users)
- **Individual Teacher Details**: [`http://127.0.0.1:8000/api/users/29`](http://127.0.0.1:8000/api/users/29)
- **Review**: [`http://127.0.0.1:8000/api/reviews`](http://127.0.0.1:8000/api/reviews)
- **Individual Review**: [`http://127.0.0.1:8000/api/reviews/1`](http://127.0.0.1:8000/api/reviews/1)
- **Enroll**: [`http://127.0.0.1:8000/api/enroll/`](http://127.0.0.1:8000/api/enroll/)
- **History**: [`http://127.0.0.1:8000/api/history/`](http://127.0.0.1:8000/api/history/)



<h2>🛠️ Installation Steps:</h2>

<p>1. Python 3.x installed.</p>

<p>2. Django installed. If not you can install it using</p>

```
pip install Django
```

<p>3. Clone the repository</p>

```
git clone https://github.com/abin0x/online-school.git
```

<p>4. Navigate to the project directory</p>

```
cd online-school
```

<p>5. Create a virtual environment</p>

```
python -m venv venv
```

<p>6. Activate the virtual environment</p>

```
venv\Scripts\activate
```

<p>7. Install the required packages</p>

```
pip install -r requirements.txt
```

<p>8. Run database migrations</p>

```
python manage.py migrate
```

<p>9. Create a superuser for accessing the admin panel</p>

```
python manage.py createsuperuser
```

<p>10. Start the Django development server</p>

```
python manage.py runserver
```

<p>11. Open your browser and go to http://127.0.0.1:8000 to access the application</p>




## Model/Schemas

The following models are used in the project:

### User
- **username**: `CharField`
- **email**: `EmailField`
- **password**: `CharField`

### Course
- **title**: `CharField`
- **description**: `TextField`
- **instructor**: `ForeignKey (User)`
- **created_at**: `DateTimeField`

### Enrollment
- **student**: `ForeignKey (User)`
- **course**: `ForeignKey (Course)`
- **enrolled_at**: `DateTimeField`

