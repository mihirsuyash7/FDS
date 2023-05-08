from flask import Flask, render_template, request, redirect
from database import Transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
import datetime
from fraud_detection import predict
import pandas as pd


logged_in = False
logged_in_detail = None
otp = None
adminpass = '12345678'
receiver = None
loginmsg = None
alert = None
pschanged = False
admincount = 0

def noneall():
    global otp
    global adminpass
    global receiver
    global loginmsg
    global pschanged
    otp = adminpass = receiver = loginmsg = None
    pschanged = False

app = Flask(__name__)

#function to load database table into a pandas dataframe
def load_data():
    engine = create_engine('sqlite:///project.sqlite').connect()    # Creating Database Engine
    df = pd.read_sql_table('transactions', engine)  # Reading Database Table into Pandas DataFrame
    print(df.head())    # Printing DataFrame
    return df   # Returning DataFrame

def getdb():
    engine = create_engine('sqlite:///project.sqlite')  # Creating Database Engine
    DBSession = sessionmaker(bind=engine)   # Creating Session for Database
    session = scoped_session(DBSession) # Creating Scoped Session for Database
    return session

@app.route('/')
def index():
    print(f"Logged In : {logged_in}\nOTP : {otp}\nAdmin Pass : {adminpass}\nReceiver : {receiver}\nLogin Msg : {loginmsg}\nPassword Changed : {pschanged}")
    return redirect('/homepage')

@app.route('/login', methods=['GET','POST'])
def login():
    message = None
    global alert
    alert = 'danger'
    global logged_in
    global logged_in_detail
    global loginmsg
    if request.method == "POST":
        login_email = request.form.get('login_email')
        login_password = request.form.get('login_password')
        print("Login Detail : ",login_email, login_password)
        if login_email == 'admin@fraud.com':
            if login_password == adminpass:
                print("Admin Login Successful")
                loginmsg = 'Admin Login Successful!'
                alert = 'success'
                logged_in = True
                logged_in_detail = {'name':'Admin', 'email':'admin@fraud.com', 'password':adminpass, 'admin':'True'}
                return redirect('/')
            else:
                print("Admin Password Not matched")
                message = 'Invalid Email or Password!'
                logged_in = False
        else:
            print("Invalid Username")
            message = 'Invalid Email or Password!'
            logged_in = False
    if not message and loginmsg:
        message = loginmsg
        alert = 'success'
        if pschanged:
            noneall()
    print(f"Logged In : {logged_in}\nOTP : {otp}\nAdmin Pass : {adminpass}\nReceiver : {receiver}\nLogin Msg : {loginmsg}\nPassword Changed : {pschanged}")
    return render_template('login1.html', title='Login', logged_in=logged_in, user=logged_in_detail, message=message, alert=alert)

@app.route('/logout')
def logout():
    global logged_in
    logged_in = False
    global alert
    alert = None
    global loginmsg
    loginmsg = None
    print(f"Logged in : {logged_in}")
    return redirect('/login')

# @app.route('/dashbard', methods=['GET','POST'])
# def dashboard():
#     global logged_in
#     global loginmsg
#     global alert
#     df = load_data()
#     if request.method == 'POST':
#         return render_template('dashboard.html', title='Dashboard', result = df.to_html(), logged_in=logged_in, message=loginmsg, alert=alert)
#     return render_template('dashboard.html', title='Dashboard', result = df.to_html(), logged_in=logged_in, message=loginmsg, alert=alert)

@app.route('/dashboard', methods=['GET','POST'])
def insert():
    isFraud = 0
    global loginmsg
    loginmsg = data = None
    global alert
    df = load_data()
    if request.method == 'POST':
        trans_type=request.form.get('trans_type') 
        trans_amt=request.form.get('trans_amt')
        trans_nameOrig=request.form.get('trans_nameOrig')
        trans_oldbalanceOrig=request.form.get('trans_oldbalanceOrg')
        trans_newbalanceOrig=request.form.get('trans_newbalanceOrig')
        trans_nameDest=request.form.get('trans_nameDest')
        trans_oldbalanceDest=request.form.get('trans_oldbalanceDest')
        trans_newbalanceDest=request.form.get('trans_newbalanceDest')
        
        # Creting dictionary for extracted data
        data = pd.DataFrame({
            'step': [1], 
            'type': [trans_type], 
            'amount': [trans_amt], 
            'name_orig': [trans_nameOrig], 
            'oldbalanceOrg': [trans_oldbalanceOrig], 
            'newbalanceOrig': [trans_newbalanceOrig], 
            'name_dest': [trans_nameDest], 
            'oldbalanceDest': [trans_oldbalanceDest], 
            'newbalanceDest': [trans_newbalanceDest]
            })
        if trans_type and trans_amt and trans_nameOrig and trans_oldbalanceOrig and trans_newbalanceOrig and trans_nameDest and trans_oldbalanceDest and trans_newbalanceDest:
            model_path = r'models\v1\ann_fraud_detection.h5'
            pp_path = r'models\v1\ann_fraud_detection_preprocessor.jb'
            out = predict(model_path, pp_path, data)
            print(out[0][0] > 0.5)
            if out[0][0] > 0.5:
                print('Fraud')
                isFraud = 1
            else:
                print('Not Fraud')
                isFraud = 0
            db = getdb()
            db.add(Transaction(type=trans_type, amount=trans_amt, nameOrig=trans_nameOrig, oldbalanceOrig=trans_oldbalanceOrig, newbalanceOrig=trans_newbalanceOrig, nameDest=trans_nameDest, oldbalanceDest=trans_oldbalanceDest, newbalanceDest=trans_newbalanceDest, date_time=datetime.datetime.now(), is_Fraud=isFraud))
            db.commit()
            db.close()
            print('Data Saved Successfully')
            alert = 'success'
            loginmsg = 'Data Saved Successfully!'
            # return redirect('/dashboard')
        else:
            print('Data Not Saved')
            alert = 'danger'
            loginmsg = 'Data Not Saved!'
            # return redirect('/dashboard')
    print(f"Logged In : {logged_in}")
    print(f"Data : {data}")
    return render_template('dashboard.html', title='Dashboard',fraud=isFraud, logged_in=logged_in, message = loginmsg, alert=alert, result = df.to_html())

@app.route('/homepage')
def homepage():
    return render_template('homepage1.html', title="Home", logged_in=logged_in, message = loginmsg, alert=alert)

# @app.route('/predict/fraud/<int:id>/record', methods=['GET', 'POST'])
# def predict_fraud(id):
#     db = getdb()
#     transaction = db.query(Transaction).filter_by(id=id).first()
#     if transaction:
#         # convert to data frame
#         df = pd.DataFrame([transaction.__dict__])
#         # drop the id column
#         df = df.drop(['id'], axis=1)
#         pp = r'models\\v1\\ann_fraud_detection_preprocessor.jb'
#         mp = r'models\\v1\\ann_fraud_detection.h5'
#         result = predict(model_path=mp, prepro_path=pp, data_dict=df)
#         print(result)
#         return render_template('predict_fraud.html', title="Predict Fraud", logged_in=logged_in, message = loginmsg, alert=alert, result=result)
#     else:
#         return redirect('/dashboard')


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8000, debug=True)
    app.run(host='127.0.0.1', port=8000, debug=True)