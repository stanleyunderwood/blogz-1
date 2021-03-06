from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12Kamelz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP38'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        entry_name = request.form['title']
        entry_body = request.form['body']
        new_entry = Blog(entry_name, entry_body,owner)
        db.session.add(new_entry)
        db.session.commit()

        blogs = Blog.query.filter_by(owner=owner).all()
        return redirect("/single_post?id="+ str(new_entry.id))
    
    return render_template('new_post.html')

@app.route('/single_post', methods =['POST','GET'])
def blog():
    if request.args:
        blog_id = request.args.get("id")
        blog_entry = Blog.query.get(blog_id)
    
    return render_template('single_post.html', blog=blog_entry)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/')
        else:
            flash('User not logged in, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - valdate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            #TODO - user better response messaging
            return '<h1>User already exists.</h1>'
        
    return render_template('signup.html')

@app.route('/blog', methods=['POST','GET'])
def all_blogs():
    
    entries = Blog.query.all()

    return render_template('blog.html', entries=entries)

@app.route('/singleuser', methods=['GET'])
def single_user():
    
    entries = Blog.query.filter_by(owner_id=request.args.get("owner_id")).all()

    return render_template('blog.html', entries=entries)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')
        
@app.route('/', methods=['POST', 'GET'])
def index():
        
    users = User.query.all()

    return render_template('home.html', users=users)

if __name__ == '__main__':
    app.run()