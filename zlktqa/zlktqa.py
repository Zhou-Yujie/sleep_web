# encoding utf-8
import os
from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,jsonify,send_file,make_response, Response
from werkzeug.utils import secure_filename
from exts import db
import config
import time
from models import User,Question,Answer,File
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

UPLOAD_FOLDER = 'static/uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# basedir = os.path.abspath(os.path.dirname('/Users/30728/PycharmProjects/zlktqa/static/uploads'))
# ALLOWED_EXTENSIONS = set(['txt','png','jpg','xls','JPG','PNG','xlsx','gif','GIF'])

@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by(Question.create_time.desc()).all()
    }
    return render_template('index.html',**context)

@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone,User.password == password).first()
        if user:
             session['user_id'] = user.id
             session.permanent = True
             return redirect(url_for('index'))
        else:

            return 'Mobile phone number or password is wrong. Please confirm and log in again!'

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('logout'))

@app.route('/question/', methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html', question=question_model)

@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content=content )
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))

@app.route('/register/',methods=['GET','POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter(User.telephone == telephone).first()

        if user:
            return 'This moblie number has already been registered. Please change your mobile number.'
        else:
            if password1 != password2:
                return 'The passwords are not equal. Please check and re-enter'
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
#
# @app.route('/uploads/')
# def uploads():
#     return render_template('uploads.html')
#
# @app.route('/api/uploads', methods=['POST'], strict_slashes=False)
# def api_upload():
#     file_dir = '/Users/30728/PycharmProjects/zlktqa/static/uploads'
#     if not os.path.exists(file_dir):
#         os.makedirs(file_dir)
#     f=request.files['myfile']
#     if f and allowed_file(f.filename):
#         fname=f.filename
#         ext = fname.rsplit('.', 1)[1]
#         unix_time = int(time.time())
#         new_filename = str(unix_time)+'.'+ext
#         f.save(os.path.join(file_dir, new_filename))
#
#         return jsonify({"errno": 0, "errmsg": "success"})
#     else:
#         return jsonify({"errno": 1001, "errmsg": "fail"})

@app.route('/uploads/',methods=['GET','POST'])
@login_required
def uploads():
    if request.method == 'GET':
        return render_template('uploads.html')
    else:
        f = request.files['file']
        f.save(os.path.join(os.path.dirname('uploads'), secure_filename(f.filename)))
        file = File(file_name=str(secure_filename(f.filename)))
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        file.author = user
        db.session.add(file)
        db.session.commit()
        return redirect(url_for('downloads'))

@app.route('/download/<filename>', methods=['GET'])
def downloads_process(filename):
    dirpath = os.path.dirname('uploads')
    return send_from_directory(dirpath, filename)

@app.route('/download/')
@login_required
def downloads():
    context = {
        'files': File.query.order_by(File.create_time.desc()).all()
    }
    return render_template('downloads.html',**context)

# @app.route('/downloads/<filename>', methods=['GET'])
# def downloads(filename):
#     filename = 'ZHOU_ID.jpg.tif'
#     dirpath = os.path.join('/Users/30728/PycharmProjects/zlktqa/static/uploads')
#     send_from_directory(dirpath, filename)
#     return render_template('downloads.html')

# @app.route("/download", methods=['GET'])
# def downloads():
#     return send_from_directory('/Users/30728/PycharmProjects/zlktqa/static/uploads', 'ZHOU_ID.jpg', as_attachment=True)
@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 1
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/indexx/')
def indexx():
    return render_template('indexx.html')

if __name__ == '__main__':
    app.run()
