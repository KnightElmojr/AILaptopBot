from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Task
from flask_socketio import SocketIO, emit
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('home.html')

@app.route("/chat")
def chat():
    return render_template("chat.html")
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    name = None
    if request.method == 'POST':
        name = request.form.get('name')
    return render_template('form.html', name=name)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('login.html', register_mode=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            return "Невірний логін або пароль", 401
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST' and current_user.is_authenticated:
        title = request.form.get('title')
        new_task = Task(title=title, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        socketio.emit('receive_message', {
            'user': 'Система',
            'msg': f'Користувач {current_user.username} додав нове завдання: {title}'
        })

    all_tasks = Task.query.all()
    return render_template('tasks.html', tasks=all_tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task_api():
    data = request.json
    new_task = Task(title=data.get('title'), description=data.get('description'))
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created"}), 201


@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = db.session.get(Task, id)

    if task:
        if task.user_id == current_user.id:
            db.session.delete(task)
            db.session.commit()
            return redirect(url_for('tasks'))
        else:
            return "У вас немає прав для видалення цього завдання", 403

    return "Завдання не знайдено", 404

@app.route('/api/tasks', methods=['GET'])
def get_tasks_api():
    tasks = Task.query.all()
    return jsonify([{"id": t.id, "title": t.title} for t in tasks])


@app.route('/api/tasks/<int:id>', methods=['PUT'])
def edit_task_api(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.json
    if 'title' in data:
        task.title = data['title']

    db.session.commit()
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return "У вас немає прав для редагування цього завдання", 403
    if request.method == 'POST':
        task.title = request.form.get('title')
        db.session.commit()
        return redirect(url_for('tasks'))
    return render_template('edit.html', task=task)


@socketio.on('send_message')
def handle_message(data):
    username = current_user.username if current_user.is_authenticated else "Гість"
    msg = data.get('message')

    emit('receive_message', {'user': username, 'msg': msg}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)