import json,requests,random,string
from functools import wraps
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash 
# local imports follows below
from bookapp import app,csrf,mail,Message
from bookapp.models import db,Book,User,Category,State,Lga,Reviews,Donation
from bookapp.forms import *

def generate_string(howmany):
    x=random.sample(string.digits,howmany)
    return '.join'


@app.route("/sendmail")
def send_email():
    file=open('requirements.txt')
    msg= Message(subject="Adding Heading to Email From BookWorm",sender="From BookWorm Website",recipients=["teniakintokunbo@gmail.com"],body="<h1>Thank you for contacting us</h1>")
    msg.html="""<h1>Welcome Home!</h1>
    <img src="https://images.pexels.com/photos/214574/pexels-photo-214574.jpeg?auto=compress&cs=tinysrgb&w=600"><hr>"""
    msg.attach("saved_as.txt","application/text",file.read())
    mail.send(msg)
    return "done"


@app.route("/favourite")
def favourite_topics():
    bootcamp={'name':'eniola','topics':['html','css','python']}
    category=[]
    cats=db.session.query(Category).all()
    for c in cats:
        category.append(c.cat_name)
    return json.dumps(category)


@app.route("/contact/")
def ajax_contact():
    data="I am a string coming from the server"
    return render_template("user/ajax_test.html",data=data)

@app.route("/submission/")
def ajax_submission():
    '''This route will be visited by ajax silently'''
    user = request.args.get('fullname')
    if user != "" and user != None:
        return f"Thank you {user} for completing the form"
    else:
        return "Please complete the form"
    
@app.route('/checkusername',methods=['post','get'])
def checkusername():
    mail=request.form.get('usermail')
    check=db.session.query(User).filter(User.user_email==mail).first()
    if check:  
        return "Email Taken"
    else:
        return "Email is okay,go ahead"



@app.route("/ajaxopt/", methods=['GET','POST'])
def ajax_option():
    cform=ContactForm()
    if request.method=='GET':
        return render_template("user/ajax_option.html",cform=cform)
    else:
        email=request.form.get('email')#the name attribute on the form input because we used either form.serialize or form.data
        return f"Thank you, your email has been added {email}"


@app.route("/dependent/")
def dependent_dropdown():
    states=db.session.query(State).all()
    return render_template("user/show_states.html",states=states)



@app.route("/lga/<stateid>")
def load_lgas(stateid):
    records=db.session.query(Lga).filter(Lga.state_id==stateid).all()
    str2return ="<select class='form-control' name='lga'>"
    for r in records:
        optstr =f"<option value='{r.lga_id}'>"+ r.lga_name+"</option>"
        str2return =str2return + optstr
    str2return =str2return + "</select>"
    return str2return



############
#This is a decorator
def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get("userloggedin") !=None:
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect("/login")
    return  login_check


@app.route("/profile",methods=['GET','POST'])
@login_required
def edit_profile():
    id=session.get("userloggedin")
    userdeets=db.session.query(User).get(id)
    pform=ProfileForm()
    if request.method =="GET":
        return render_template("user/edit_profile.html",pform=pform,userdeets=userdeets)
    else:
        if pform.validate_on_submit():
            fullname = request.form.get('fullname')
            userdeets.user_fullname = fullname
            db.session.commit()
            flash("profile updated")
            return redirect('/dashboard')
        else:
            return render_template("user/edit_profile.html",pform=pform,userdeets=userdeets)


@app.route("/")
def home_page():
    books=db.session.query(Book).filter(Book.book_status=="1").limit(4).all()
    #connect to the endpoint http://127.0.0.1:5000/api/v1.0/listall to connect data of books,pass it to the template and dispaly on the template
    try:
        response=requests.get('http://127.0.0.1:5000/api/v1.0/listall')
        #import requests
        rsp=json.loads(response.text)
    except:
        rsp=None #if the server is unreachable
    return render_template("user/home_page.html",books=books,rsp=rsp)



@app.route("/submit_review/",methods=['POST'])
@login_required
def submit_review():#retrieve form data and insert into db
    title=request.form.get('title')
    content=request.form.get('content')
    userid = session['userloggedin']
    book =request.form.get('book')
    br =Reviews(rev_title=title,rev_text=content, rev_userid=userid, rev_bookid=book)
    db.session.add(br)
    db.session.commit()
    retstr=f"""<article class="blog-post">
        <h5 class="blog-post-title">{title}</h5>
        <p class="blog-post-meta">Reviewed just now by <a href="#">{br.reviewby.user_fullname}</a></p>

        <p>{content}</p>
        <hr> 
    </article>"""
    return retstr


@app.route("/myreviews")
@login_required
def myreviews():
    id=session['userloggedin']
    userdeets=db.session.query(User).get(id)
    return render_template('user/myreviews.html',userdeets=userdeets)



@app.route("/book/details/<id>")
def book_details(id):
    book=Book.query.get_or_404(id)
    return render_template("user/reviews.html",book=book)


@app.route("/register",methods=['POST','GET'])
def register():
    regform=RegForm()
    if request.method=='GET':
        return render_template("user/signup.html",regform=regform)
    else:
        if regform.validate_on_submit():
            fullname=regform.fullname.data
            email=regform.email.data
            pwd=regform.pwd.data
            hashed_pwd=generate_password_hash(pwd)
            u=User(user_fullname=fullname,user_email=email,user_pwd=hashed_pwd)
            db.session.add(u)
            db.session.commit()
            flash ("An account has been created for you.Please Login")
            return redirect('/login')
        else:
             return render_template("user/signup.html",regform=regform)
        
@app.route("/login",methods=['POST','GET'])
def login():
    regform=RegForm()
    if request.method=='GET':
        return render_template("user/loginpage.html")
    else:
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        deets=db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd=deets.user_pwd
            if check_password_hash(hashed_pwd,pwd) ==True:
                session['userloggedin'] =deets.user_id
                return redirect("/dashboard")
            else:
                flash("Invalid credentials,try again")
                return redirect("/login")
        else:
            flash("Invalid credentials,try again")
            return redirect("/login")
        
@app.route("/logout")
def logout():
    if session.get('userloggedin')!=None:
        session.pop('userloggedin',None)
    return redirect("/")




@app.route("/dashboard")
def dashboard():
    if session.get('userloggedin') != None:
        id=session.get('userloggedin')
        userdeets=User.query.get(id)
        return render_template("user/dashboard.html",userdeets=userdeets)
    else:
        flash("You need to login to access this page")
        return redirect("/login")


@app.route("/viewall/")
def viewall():
    books=db.session.query(Book).filter(Book.book_status=="1").all()
    return render_template("user/viewall.html",books=books)


@app.route("/changedp/",methods=['GET','POST'])
@login_required
def changedp():
    id=session.get('userloggedin')
    userdeets =db.session.query(User).get(id)
    dpform=DpForm()
    if request.method =="GET":
        return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)
    else:
        if dpform.validate_on_submit():
            pix= request.files.get('dp')
            filename=pix.filename #we can rename to avaoid name clash
            pix.save(app.config['USER_PROFILE_PATH']+filename)# this has been defined in config
            userdeets.user_pix= filename
            db.session.commit()
            flash("Profile picture updated")
            return redirect(url_for('dashboard'))
        else:
            return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)


@app.route("/donate",methods=['POST','GET'])
@login_required
def donation():
    donform=DonationForm()
    if request.method =='GET':
        deets =db.session.query(User).get(session['userloggedin'])
        return render_template("user/donation_form.html",donform=donform,deets=deets)
    else:
        if donform.validate_on_submit():
            amt=float(donform.amt.data) *100
            donor=donform.fullname.data
            email=donform.email.data
            ref="BW"+str(generate_string(8))
            donation=Donation(don_amt=amt,don_userid=session['userloggedin'],don_email=email,
            don_fullname=donor,don_status='pending',don_refno=ref)
            db.session.add(donation)
            db.session.commit()
            session['trxno']=ref
            return redirect("/confirm_donation")
        else:
            deets =db.session.query(User).get(session['userloggedin'])
            return render_template("user/donation_form.html",donform=donform,deets=deets)


@app.route("/confirm_donation/")
@login_required
def confirm_donation():
    '''We want to display the details of the transaction saved from previous page'''
    deets=db.session.query(User).get(session['userloggedin'])
    if session.get('trxno') == None: #means they are visiting here directly
        flash("Please Complete this form",category='error')
        return redirect("/donate")
    else:
        donation_deets=Donation.query.filter(Donation.don_refno==session['trxno']).first()
        return render_template("user/donation_confirmation.html",donation_deets=donation_deets,deets=deets)

@app.route("/initialize/paystack/")
@login_required
def initialize_paystack():
    deets=User.query.get(session['userloggedin'])
    #transaction details
    refno=session.get('trxno')
    transaction_deets=db.session.query(Donation).filter(Donation.don_refno==refno).first()
    #make a curl request to the paystack endpoint
    url="http://api.paystack.co/transaction/initialize"
    headers={"Content-Type":"application/json","Authorization":"Bearer pk_test_54b3d8def994915e5e82fdcbf35602b8f64a0f37"}
    data={"email":deets.user_email,"amount":transaction_deets.don_amt,"refrence":refno}
    response = requests.post(url,headers=headers,data=json.dumps(data))
    #extract json from the response coming from paystack
    rspjson = response.json()
    # return rspjson
    if rspjson['status'] == True:
        redirectURL = rspjson['data']['authorization_url']
        return redirect(redirectURL) #paystack payment page will load
    else:
        flash("Please complete the form again")
        return redirect('/donate')

@app.route("/landing")
@login_required
def landing_page():
    refno=session.get('trxno')
    transaction_deets=db.session.query(Donation).filter(Donation.don_refno==refno).first()
    url="https://api.paystack.co/transaction/verify/"+transaction_deets.don_refno
    headers = {"Content-Type":"application/json","Authorization":"Bearer pk_test_54b3d8def994915e5e82fdcbf35602b8f64a0f37"}
    response = requests.get(url,headers=headers)
    rspjson = json.loads(response.text)
    if rspjson['status'] == True:
        paystatus = rspjson['data']['gateway_response']
        transaction_deets.don_status = 'Paid'
        db.session.commit()
        return redirect('/dashboard') 
    else:
        flash("Payment Failed")
        return redirect('/reports') #display all the payment reports


@app.after_request
def after_request(response):
    # To solvem the problem of loggedout user's details being cached in the browser
    response.headers["cache-control"]="no-cache, no-store, must-validate"
    return response
