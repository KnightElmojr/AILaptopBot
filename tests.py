import unittest
from web_app import app, db
from models import User, Task
from flask_login import current_user
from werkzeug.security import generate_password_hash

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        """Налаштування перед кожним тестом: створення бази в пам'яті"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Очищення після кожного тесту"""
        with app.app_context():
            db.session.remove()
            db.drop_all()


    def test_registration(self):
        """Перевірка реєстрації нового користувача"""
        response = self.app.post('/register', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)

    def test_login_logout(self):
        """Перевірка входу та виходу з системи"""
        self.app.post('/register', data={'username': 'user1', 'password': '123'}, follow_redirects=True)

        response = self.app.post('/login', data={'username': 'user1', 'password': '123'}, follow_redirects=True)
        self.assertIn(b'/logout', response.data)

        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'/login', response.data)


    def test_add_task_authorized(self):
        """Перевірка додавання завдання авторизованим користувачем"""
        self.app.post('/register', data={'username': 'dev', 'password': '123'})
        self.app.post('/login', data={'username': 'dev', 'password': '123'})
        self.app.post('/tasks', data={'title': 'Вивчити Flask'}, follow_redirects=True)

        with app.app_context():
            task = Task.query.filter_by(title='Вивчити Flask').first()
            self.assertIsNotNone(task)

    def test_edit_task(self):
        """Перевірка редагування існуючого завдання"""
        with app.app_context():
            hashed_pw = generate_password_hash('123')
            u = User(username='admin', password=hashed_pw)
            db.session.add(u)
            db.session.commit()
            t = Task(title='Стара назва', user_id=u.id)
            db.session.add(t)
            db.session.commit()
            task_id = t.id
        self.app.post('/login', data={'username': 'admin', 'password': '123'})

        response = self.app.post(f'/edit/{task_id}', data={'title': 'Нова назва'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            db.session.expire_all()
            updated_task = db.session.get(Task, task_id)
            self.assertEqual(updated_task.title, 'Нова назва')

    def test_delete_task(self):
        """Перевірка видалення завдання"""
        with app.app_context():

            hashed_password = generate_password_hash('123')
            u = User(username='tester', password=hashed_password)
            db.session.add(u)
            db.session.commit()

            t = Task(title='На видалення', user_id=u.id)
            db.session.add(t)
            db.session.commit()
            task_id = t.id

        self.app.post('/login', data={'username': 'tester', 'password': '123'}, follow_redirects=True)
        response = self.app.get(f'/delete/{task_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            db.session.expire_all()
            deleted_task = db.session.get(Task, task_id)
            self.assertIsNone(deleted_task)

    def test_api_get_tasks(self):
        """Перевірка отримання списку завдань через REST API"""
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')


if __name__ == '__main__':
    unittest.main()