from flask import Flask, render_template, flash, redirect, request, session
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import os

app = Flask(__name__)
Bootstrap(app)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def index():
    # GET / home page links to all blogs listed here
    return render_template('index.html')


@app.route('/about/')
def about():
    # GET /about load the about page of the app
    return render_template('about.html')


@app.route('/blogs/<int:id>/')
def blogs(id):
    # GET /blogs/<int: id>  loads the blogpost with the given id
    return render_template('blogs.html', blog_id=id)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # GET /register loads a form to register a user
    # POST /register validates the form details and creates a new user in the db
    if request.method == 'POST':
        user_details = request.form
        if user_details['password'] != user_details['confirm_password']:
            flash('Passwords do not match! Try again.', 'danger')
            return render_template('register.html')
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user(first_name, last_name, username, email, password) "\
        "VALUES(%s,%s,%s,%s,%s)",(user_details['first_name'], user_details['last_name'], \
        user_details['username'], user_details['email'], generate_password_hash(user_details['password'])))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # GET /login    loads a form for user login
    # POST /login   validates credentials entered by the user and logs them in
    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        cursor = mysql.connection.cursor()
        result_value = cursor.execute("SELECT * FROM user WHERE username = %s", ([username]))
        if result_value > 0:
            user = cursor.fetchone()
            if check_password_hash(user['password'], user_details['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                flash('Welcome ' + session['first_name'] + '! You have successfully logged in!', 'success')
            else:
                cursor.close()
                flash('Password does not match', 'danger')
                return render_template('login.html')
        else:
            cursor.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cursor.close()
        return redirect('/')
    return render_template('login.html')


@app.route('/write-blog/', methods=['GET', 'POST'])
def write_blog():
    # GET /write-blog loads a form with which the user can write a blogpost
    # POST /write-blog creates a new blog in the database
    return render_template('write-blog.html')


@app.route('/my-blogs/')
def my_blogs():
    # GET /my-blogs  list of all links of blogs written by the logged in user
    return render_template('my-blogs.html')


@app.route('/edit-blog/<int:id>/', methods=['GET', 'POST'])
def edit_blog(id):
    # GET /edit-blog/<int: id> loads a form with content from blogpost of the id mentioned
    # POST /edit-blog/<int: id> updates the blogpost with the given id
    return render_template('edit-blog.html', blog_id=id)


@app.route('/delete/<int:id>/', methods=['POST'])
def delete_blog():
    # POST /delete-blog/<int: id> deletes the blogpost with the given id
    return 'success', 200


@app.route('/logout/')
def logout():
    # GET /logout logs out the current user
    return render_template('logout.html')


if __name__ == '__main__':
    app.run()
