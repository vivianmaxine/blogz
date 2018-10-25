from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)  # creates database object


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(50000))

    def __init__(self, title, entry):
        self.title = title
        self.entry = entry

    def __repr__(self):
        return '<BlogPost %r>' % self.title


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
        post_title = request.form['title']
        post_entry = request.form['entry']

        new_post = BlogPost(title=post_title, entry=post_entry)

        db.session.add(new_post)
        db.session.commit()

    posts = BlogPost.query.all()

    return render_template('index.html', title="Vivian's Blog", posts=posts)


@app.route('/newpost', methods=['POST', 'GET'])
def create_post():
    title_error = ''
    entry_error = ''

    if request.method == 'POST':
        new_post_title = request.form['new_title']
        new_post_entry = request.form['new_entry']

        if new_post_title == '':
            title_error = 'Please enter a title for your blog post.'

        if new_post_entry == '':
            entry_error = 'Please enter content for your blog post.'

        if title_error == '' and entry_error == '':
            new_post = BlogPost(title=new_post_title, entry=new_post_entry)

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
