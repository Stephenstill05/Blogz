from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hi'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(750))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

def verified(text):
    if len(text) >= 3 and len(text) <= 20 and not ' ' in text:
        return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes=['login','signup','blog','index','static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/newpost")
def blog_posts():
    return render_template("/newpost.html", title="New Post")

@app.route('/newpost', methods=['POST','GET'])
def newpost():

    title = request.form['title']
    body = request.form['body']
    owner = User.query.filter_by(username=session['username']).first()
        
    if len(title)==0 and len(body)==0:
        flash('title and body are left blank')
        return redirect ('/newpost')
            
    elif len(title)==0:
        flash('title is left blank')
        return redirect ('/newpost')

    elif len(body)==0:
        flash('body is left blank')
        return redirect ('/newpost')

    else:
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_blog.id)) 

    return redirect("/newpost")    

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    blogs = Blog.query.all()

    
   
    if blog_id:
        blog_posts = Blog.query.filter_by(id=blog_id).first()
        return render_template('singlepost.html', Title='Single Blog', blog_posts=blog_posts, username=blog_posts.owner.username)
    if user_id:
        entries=Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleuser.html', entries=entries)
    return render_template('blog.html', blogs=blogs)

@app.route('/')
def index():
    users=User.query.all()
    return render_template('index.html',users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']
        
        if len(username)==0:
            flash('username cannot be blank')
            return redirect('/signup')
        elif len(password)==0:
            flash('password cannot be blank')
            return redirect('/signup')
        elif not verified(username):
            flash('username must be between 3 and 20 characters with no spaces')
            return redirect('/signup')
        elif not verified(password):
            flash('password must be between 3 and 20 characters with no spaces')
            return redirect('/signup')
        elif password != verify_password:
            flash('passwords do not match')
            return redirect('/signup')
        else:
            new_user=User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            return redirect('/newpost')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password==password:
            session['username']=username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('user password incorrect or user does not exist')

    return render_template("login.html")
    


@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['username']
    return redirect('/')


def verified(var):
    if len(var) >= 3 and len(var) <= 20 and not ' ' in var:
        return True
    else:
        return False

def email_ver(letters):
    if len(letters) == 0:
        return True
    elif verified(letters) and '@' in letters and '.' in letters:
        return True
    else:
        return False
















if __name__=='__main__':
    app.run()

    

    