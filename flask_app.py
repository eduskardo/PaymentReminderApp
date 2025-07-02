from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# It is recommended to set a secure secret key in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/payments')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    entities = db.relationship('PaymentEntity', backref='user', lazy=True)

class PaymentEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    frequency = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    history = db.relationship('PaymentHistory', backref='entity', lazy=True)

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('payment_entity.id'), nullable=False)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    entities = PaymentEntity.query.filter_by(user_id=user.id).all()
    return render_template('index.html', user=user, entities=entities)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Usuario ya existe')
        hashed = generate_password_hash(password)
        user = User(username=username, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/entity/add', methods=['GET', 'POST'])
def add_entity():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        amount = float(request.form['amount'])
        due_date = request.form['due_date']
        frequency = request.form['frequency']
        entity = PaymentEntity(
            name=name,
            description=description,
            amount=amount,
            due_date=due_date,
            frequency=frequency,
            user_id=session['user_id']
        )
        db.session.add(entity)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('entity_form.html')

@app.route('/entity/<int:entity_id>')
def view_entity(entity_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    entity = PaymentEntity.query.get_or_404(entity_id)
    history = PaymentHistory.query.filter_by(entity_id=entity.id).all()
    return render_template('entity_detail.html', entity=entity, history=history)

@app.route('/entity/<int:entity_id>/pay', methods=['POST'])
def register_payment(entity_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    amount = float(request.form['amount'])
    payment = PaymentHistory(date=db.func.now(), amount=amount, entity_id=entity_id)
    db.session.add(payment)
    db.session.commit()
    return redirect(url_for('view_entity', entity_id=entity_id))

@app.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    total_due = db.session.query(db.func.sum(PaymentEntity.amount)).filter_by(user_id=user_id).scalar() or 0
    total_paid = db.session.query(db.func.sum(PaymentHistory.amount)).join(PaymentEntity).filter(PaymentEntity.user_id==user_id).scalar() or 0
    return render_template('stats.html', total_due=total_due, total_paid=total_paid)

if __name__ == '__main__':
    app.run(debug=True)
