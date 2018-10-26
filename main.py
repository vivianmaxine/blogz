from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)  # creates database object

app.secret_key = '&VAptc8mjJj^CL$S'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog_posts = db.relationship('BlogPost', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(50000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, entry, owner):
        self.title = title
        self.entry = entry
        self.owner = owner

    def __repr__(self):
        return '<BlogPost %r>' % self.title


@app.route('/', methods=['POST', 'GET'])
def blog():
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        post_title = request.form['title']
        post_entry = request.form['entry']
        new_post = BlogPost(
            title=post_title, entry=post_entry, owner=owner)
        db.session.add(new_post)
        db.session.commit()

    posts = BlogPost.query.filter_by(owner=owner).all()


    return render_template('index.html', title="Blogz", posts=posts)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify_pw = request.form['verify']
        # TODO: VALIDATE THE DATA
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            # TODO: REMEMBER THE USER
            session['email'] = email
            return redirect('/')
        else:
            return "<h1>User Already Exists! :(</h1>"
    return render_template('register.html')


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # TODO: REMEMBER USER LOGGED IN
            session['email'] = email
            # TODO: ADD VALIDATION
            flash("Success! You are Logged in.", 'success')
            return redirect('/')
        else:
            # TODO: TELL THEM WHY LOGIN FAILED
            flash("Incorrect password or user does not exist", 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/newpost', methods=['POST', 'GET'])
def create_post():
    title_error = ''
    entry_error = ''

    if request.method == 'POST':
        new_post_title = request.form['new_title']
        new_post_entry = request.form['new_entry']
        owner = User.query.filter_by(email=session['email']).first()

        if new_post_title == '':
            title_error = 'Please enter a title for your blog post.'

        if new_post_entry == '':
            entry_error = 'Please enter content for your blog post.'

        if title_error == '' and entry_error == '':
            new_post = BlogPost(title=new_post_title, entry=new_post_entry, owner=owner)

            db.session.add(new_post)
            db.session.commit()

            return redirect('/blogpost?id={0}'.format(new_post.id))

    return render_template(
        'newpost.html', title="Add a New Post", title_error=title_error,
        entry_error=entry_error)


@app.route('/blogpost')
def display_single_post():
    post_id = request.args.get('id')

    post = BlogPost.query.get(post_id)

    return render_template('blogpost.html', title="Blog Post", post=post)

if __name__ == "__main__":
    app.run()
