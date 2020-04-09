from flask import Flask, render_template, flash, redirect, request, session
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
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

CKEditor(app)

@app.route('/')
def index():
    # GET / home page links to all blogs listed here
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM blog")
    if result_value > 0:
        blogs = cursor.fetchall()
        cursor.close()
        return render_template('index.html', blogs=blogs)
    cursor.close()
    return render_template('index.html', blogs=None)


@app.route('/about/')
def about():
    # GET /about load the about page of the app
    return render_template('about.html')


@app.route('/blogs/<int:id>/')
def blogs(id):
    # GET /blogs/<int: id>  loads the blogpost with the given id
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog = cursor.fetchone()
        return render_template('blogs.html', blog=blog)
    return 'Blog not found'


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


@app.route('/write/', methods=['GET', 'POST'])
def write_blog():
    # GET /write-blog loads a form with which the user can write a blogpost
    # POST /write-blog creates a new blog in the database
    if request.method == 'POST':
        blog_post = request.form
        title = blog_post['title']
        body = blog_post['body']
        author = session['first_name'] + ' ' + session['last_name']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO blog(title, body, author) VALUES(%s, %s, %s)", (title, body, author))
        mysql.connection.commit()
        cursor.close()
        flash('Successfully posted new blog', 'success')
        return redirect('/')
    return render_template('write-blog.html')


@app.route('/my-blogs/')
def my_blogs():
    # GET /my-blogs  list of all links of blogs written by the logged in user
    author = session['first_name'] + ' ' + session['last_name']
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM blog WHERE author = %s", [author])
    if result_value > 0:
        my_blogs = cursor.fetchall()
        return render_template('my-blogs.html', my_blogs=my_blogs)
    else:
        return render_template('my-blogs.html', my_blogs=None)


@app.route('/edit/<int:id>/', methods=['GET', 'POST'])
def edit_blog(id):
    # GET /edit-blog/<int: id> loads a form with content from blogpost of the id mentioned
    # POST /edit-blog/<int: id> updates the blogpost with the given id
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cursor.execute("UPDATE blog SET title = %s, body = %s WHERE blog_id = %s",(title, body, id))
        mysql.connection.commit()
        cursor.close()
        flash('Blog updated successfully', 'success')
        return redirect('/blogs/{}'.format(id))
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog_form = cursor.fetchone()
        return render_template('edit-blog.html', blog_form=blog_form)


@app.route('/delete/<int:id>/')
def delete_blog(id):
    # POST /delete-blog/<int: id> deletes the blogpost with the given id
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    mysql.connection.commit()
    flash("Your blog has been deleted", 'success')
    return redirect('/my-blogs/')


@app.route('/logout/')
def logout():
    # GET /logout logs out the current user
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')


if __name__ == '__main__':
    app.run()
