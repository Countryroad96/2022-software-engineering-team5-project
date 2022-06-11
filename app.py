import os  # 디렉토리 절대 경로
from flask import Flask, flash
from flask import render_template  # template폴더 안에 파일을 쓰겠다
from flask import request  # 회원정보를 제출할 때 쓰는 request, post요청 처리
from flask import redirect # 리다이렉트
from models import db
from models import User, Product
from flask import session  # 세션
from flask_wtf.csrf import CSRFProtect  # csrf
from forms import RegisterForm, LoginForm, SellingForm
from werkzeug.utils import secure_filename
from PIL import Image
app = Flask(__name__)

default_file_path = 'static/src/img/'


@app.route('/')
def mainpage():
    userid = session.get('userid', None)
    products = Product.query.all()
    return render_template('main.html', userid=userid, products=products)

@app.route('/selling', methods=['GET', 'POST'])
def selling():
    form = SellingForm()
    userid = session.get('userid', None)
    if not userid:
        message = '로그인 후 이용 가능합니다'
        flash(message)
        return redirect('/')
    
    if form.validate_on_submit():
        filename = secure_filename(form.picture.data.filename)
        
        product_table = Product(session.get('userid', None),
                                form.data.get('title'),
                                form.data.get('keyword'),
                                form.data.get('price'),
                                form.data.get('contact'),
                                filename,
                                form.data.get('detail'))
        db.session.add(product_table)
        db.session.commit()
        
        form.picture.data.save(default_file_path + str(product_table.id) + filename)
        
        message = '판매글이 저장되었습니다'
        flash(message)
        return redirect('/')
    return render_template('selling.html', form=form)

@app.route('/update/<product_id>', methods=['GET', 'POST'])
def update(product_id):
    form = SellingForm()
    userid = session.get('userid', None)
    
    if product_id:
        product = Product.query.get(product_id)
        if not product:
            return redirect('/')
    else:
        return redirect('/')
    
    if not userid:
        message = '로그인 후 이용 가능합니다'
        flash(message)
        return redirect('/')
    elif not userid == product.userid:
        message = '작성자만 수정이 가능합니다'
        flash(message)
        return redirect('/')
    
    form.title.data = product.title
    form.keyword.data = product.keyword
    form.price.data = product.price
    form.contact.data = product.contact
    #form.picture.data = Image.open(default_file_path + product_id + product.picture)
    form.detail.data = product.detail
    #print(default_file_path + product_id + product.picture)
    #print(Image.open(default_file_path + product_id + product.picture))
    
    if form.validate_on_submit():
        filename = secure_filename(form.picture.data.filename)
        
        product.title = form.data.get('title')
        product.keyword = form.data.get('keyword')
        product.price = form.data.get('price')
        product.contact = form.data.get('contact')
        product.picture = filename
        product.detail = form.data.get('detail')
        db.session.commit()
        
        form.picture.data.save(default_file_path + str(product.id) + filename)
        
        message = '판매글이 저장되었습니다'
        flash(message)
        return redirect('/')
    
    return render_template('update.html', form=form, product=product)\

@app.route('/delete/<product_id>')
def delete(product_id):
    userid = session.get('userid', None)
    
    if product_id:
        product = Product.query.get(product_id)
        if not product:
            return redirect('/')
    else:
        return redirect('/')
    
    if not userid:
        message = '로그인 후 이용 가능합니다'
        flash(message)
        return redirect('/')
    elif not userid == product.userid:
        message = '작성자만 삭제가 가능합니다'
        flash(message)
        return redirect('/')
    
    db.session.delete(product)
    db.session.commit()
    
    message = '삭제가 완료되었습니다'
    flash(message)
    return redirect('/')

@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    form = RegisterForm()
    userid = session.get('userid', None)
    following_list = None
    
    if userid:
        following_list = User.query.filter_by(userid=userid).first().get_following()

    product = Product.query.get(product_id)
    return render_template('product.html', product=product, userid=userid, following_list=following_list, form=form)

@app.route('/setpurchased', methods=['POST'])
def setpurchased():
    product_id = request.form['product_id']
    temp = Product.query.get(product_id)
    
    if not temp:
        message = '잘못된 접근입니다'
        flash(message)
        return redirect('/')
    
    temp.set_purchased()
    message = '판매완료 변경이 완료되었습니다'
    flash(message)
    
    return redirect('/product/'+request.form['product_id'])


@app.route('/mypage')
def mypage():
    userid = session.get('userid', None)
    return render_template('mypage.html', userid=userid)

@app.route('/sellinglist/<targetid>')
def sellingList(targetid):
    products = Product.query.filter_by(userid=targetid).all()
    return render_template('sellingList.html', products=products)

@app.route('/followinglist')
def followingList():
    userid = session.get('userid', None)
    
    if not userid:
        message = '로그인 후 이용 가능합니다'
        flash(message)
        return redirect('/')
    
    temp = User.query.filter_by(userid=userid).first()
    
    following_ids = temp.get_following()
    
    return render_template('followingList.html', following_ids=following_ids)

@app.route('/register', methods=['GET', 'POST'])    # GET(정보보기), POST(정보수정) 메서드 허용
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # 유효성 검사. 내용 채우지 않은 항목이 있는지까지 체크
        message = None
        user = User.query.filter_by(userid=form.data.get('userid')).first()
        if user:
            message = '이미 존재하는 아이디 입니다.'
            flash(message)
        else:
            message = '회원가입 성공'
            usertable = User(form.data.get('userid'),
                            form.data.get('password'))
            db.session.add(usertable)  # DB저장
            db.session.commit()  # 변동사항 반영
            flash(message)
            return redirect('/')
    return render_template('register.html', form=form)  # form이 어떤 form인지 명시한다

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 로그인폼
    if form.validate_on_submit():  # 유효성 검사
        error = None
        user = User.query.filter_by(userid=form.data.get('userid')).first()
        if not user:
            error = '존재하지 않는 사용자입니다.'
        elif not user.check_password(form.data.get('password')):
            error = '비밀번호가 올바르지 않습니다.'
        if error is None:
            print('{}가 로그인 했습니다'.format(form.data.get('userid')))
            session.clear()
            session['userid'] = form.data.get('userid')  # form에서 가져온 userid를 세션에 저장
            return redirect('/')  # 성공하면 main.html로
        flash(error)
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

@app.route('/follow', methods=['POST'])
def follow():
    userid = session.get('userid', None)
    targetid = request.form['value']
    
    if not userid:
        message = '로그인 후 이용 가능합니다'
        flash(message)
        return redirect('/')
    
    temp = User.query.filter_by(userid=userid).first()
    
    if not User.query.filter_by(userid=targetid).first():
        error = '존재하지 않는 사용자입니다.'
        flash(error)
        return redirect('/')
    
    temp.add_following(targetid)
    db.session.commit()
    flash('팔로우 성공')
    return redirect('/product/'+request.form['product_id'])

@app.route('/unfollow/', methods=['POST'])
def unfollow():
    userid = session.get('userid', None)
    targetid = request.form['value']
    
    if not userid:
        message = '로그인 후 이용 가능합니다'
        flash(message)
        return redirect('/')
    
    temp = User.query.filter_by(userid=userid).first()
    
    if not User.query.filter_by(userid=targetid).first():
        error = '존재하지 않는 사용자입니다.'
        flash(error)
        return redirect('/')
    
    temp.remove_following(targetid)
    db.session.commit()
    flash('언팔로우 성공')
    return redirect('/product/'+request.form['product_id'])


if __name__ == "__main__":
    # 데이터베이스---------
    basedir = os.path.abspath(os.path.dirname(__file__))  # 현재 파일이 있는 디렉토리 절대 경로
    dbfile = os.path.join(basedir, 'db.sqlite')  # 데이터베이스 파일을 만든다

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile   # 사용자에게 정보 전달완료하면 teadown. 그 때마다 커밋=DB반영
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 추가 메모리를 사용하므로 꺼둔다
    app.config['SECRET_KEY'] = 'secretkey'  # 해시값은 임의로 적음

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)  # app설정값 초기화
    db.app = app  # Models.py에서 db를 가져와서 db.app에 app을 명시적으로 넣는다
    db.create_all()  # DB생성

    app.run(host="127.0.0.1", port=5000, debug=True)
