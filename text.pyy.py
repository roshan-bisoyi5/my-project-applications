from flask import Flask,render_template,request,flash,session,redirect,url_for
import mysql.connector
import pandas as pd
from pytz import timezone
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
db=mysql.connector.connect(user='root',port=3306,database="bank_transaction",charset="utf8")
cur=db.cursor()
app=Flask(__name__)
app.config['SECRET_KEY']='@!@^&*&^*^$#$#&^%&$@%^$@$*(()&^%%'
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/contact_us')
def contact_us():
    return render_template('contact-us.html')
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')
@app.route('/reg')
def reg():
    return render_template('reg.html')
@app.route('/regback',methods=['POST','GET'])
def regback():
    if request.method=='POST':
        c=request.form['cname']
        e=request.form['email']
        p=request.form['pwd']
        a= request.form['accno']
        b=request.form['balance']

        sql="SELECT * from registration"
        result = pd.read_sql_query(sql, db)
        email1 = result['email'].values
        print(email1)
        if e in email1:
            flash("email already existed", "warning")
            return render_template('reg.html')
        else:
            import random
            sr = 'BANK'
            n = random.randint(0, 1000)
            s = sr + str(n)
            print(s)
            msg = 'Thanks for choosing online Banking.'
            otp = "Costomer Id is: "
            t = 'Regards,'
            t1 = 'Online Bank Service.'
            mail_content = msg + '\n' + otp + s +'.'+ '\n' + '\n' + t + '\n' + t1
            sender_address = 'cse.takeoff@gmail.com'
            sender_pass = 'Takeoff@123'
            receiver_address = e
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = 'E- Commerce Bank'

            message.attach(MIMEText(mail_content, 'plain'))
            ses = smtplib.SMTP('smtp.gmail.com', 587)
            ses.starttls()
            ses.login(sender_address, sender_pass)
            text = message.as_string()
            ses.sendmail(sender_address, receiver_address, text)
            ses.quit()
            sql = "INSERT INTO registration (custId,cname,email,Password,accno,balance) values(%s,%s,%s,%s,%s,%s)"
            val = (s,c, e, p, a, b)
            cur.execute(sql, val)
            db.commit()
            flash("Successfully account created and Customer ID sent to your mail please check it.", "success")
            return render_template('index.html')
    return render_template('reg.html')

@app.route('/custhome')
def custhome():
    return render_template('custhome.html')
@app.route('/login',methods=['POST', 'GET'])
def login():
    if request.method == "POST":

        email = request.form['email']
        c = request.form['custId']
        password1 = request.form['pwd']

        sql = "select * from registration where custId='%s' and email='%s' and password='%s' " % (c, email, password1)
        x = cur.execute(sql)
        print(x)
        results = cur.fetchall()
        print(results)
        # name=results[0][2]
        custId = results[0][1]
        session['email'] = email
        # session['name'] = name
        if(custId==c):
            if len(results) > 0:
                flash("Welcome ", "primary")
                sq="select cname,accno,balance from registration where email='%s' and custId='%s' "%(email,c)
                x = pd.read_sql_query(sq, db)
                cname=x.values[0][0]
                accno=x.values[0][1]
                balance=int(x.values[0][2])
                session['accno']=accno
                session['balance']=balance
                return render_template('custhome.html', msg=results[0][2],c=cname,a=accno,b=balance)

            else:
                flash("Login failed", "warning")
                return render_template('tender.html')
        else:
            flash("CustomerID value mismatches please try again", "danger")
            return render_template('index.html')

    return render_template('index.html')

@app.route('/trans')
def trans():
    return render_template('trans.html')

@app.route('/transback',methods=['POST','GET'])
def transback():
    if request.method == 'POST':
        rname = request.form['rname']
        toaccount = request.form['accno']
        conaccno = int(request.form['conaccno'])
        swift = request.form['swift']
        ctg=request.form['ctg']
        amount=request.form['amount']
        a=int(amount)
        ac=int(toaccount)
        co=int(conaccno)
        remail=request.form['remail']
        transtype=request.form['transtype']
        # date = datetime.datetime.now()
        # da=date.strftime("%x")
        # dt = date.strftime("%I:%M %p")
        # print(dt)
        accno=session.get('accno')
        bal=session.get('balance')
        email=session.get('email')
        ind_time1 = datetime.now(timezone("US/Eastern")).strftime('%m-%d-%Y %I:%M %p')
        ind_time2 = datetime.now(timezone("US/Eastern")).strftime('%H:%M:%S')
        ind_time = datetime.now(timezone("US/Eastern")).strftime('%H:%S %p')
        print(ind_time1)
        print(ind_time2)
        print(type(ind_time2))
        in_min = int(ind_time2.split(':')[0]) * 60
        in_min = in_min + int(ind_time2.split(':')[1])
        print(in_min)
        s = "select count(*),balance from registration where email='%s'" % (remail)
        x = pd.read_sql_query(s, db)
        count = x.values[0][0]
        b = int(x.values[0][1])
        t2 = b + a
        # if 359 < in_min:
        if ac == co:
            if count==1:
                sql="insert into transactions(saccno,semail,rname,remail,raccno,ctg,transtype,swift,amount,date1,time1) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val=(accno,email,rname,remail,toaccount,ctg,transtype,swift,a,ind_time1,ind_time)
                cur.execute(sql, val)
                db.commit()
                msg = 'Thanks for choosing online Banking.'
                # otp = "You have made a transaction of"
                # opt1="Your Transaction in  "
                t = 'Regards,'
                t1 = 'Online Bank Service.'
                mail_content = msg + '\n' +'$.'+amount+' is debited from A/c '+ accno + ' for '+ ctg + ' on ' + ind_time1 +' . '+'\n' + '\n' + t + '\n' + t1
                sender_address = 'cse.takeoff@gmail.com'
                sender_pass = 'Takeoff@123'
                receiver_address = email
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'Commerce Bank'
                message.attach(MIMEText(mail_content, 'plain'))
                ses = smtplib.SMTP('smtp.gmail.com', 587)
                ses.starttls()
                ses.login(sender_address, sender_pass)
                text = message.as_string()
                ses.sendmail(sender_address, receiver_address, text)
                ses.quit()

                total=bal-a;
                sq="update registration set balance='%s' where email='%s'"%(total,email)
                cur.execute(sq)
                db.commit()

                sq1 = "update registration set balance='%s' where email='%s'" % (t2, remail)
                cur.execute(sq1, db)
                db.commit()
                msg = 'You have received '
                otp = "Credited by "
                t = 'Regards,'
                t1 = 'Online Bank Service.'
                mail_content = msg +amount+' $ .'+otp+ accno +' on ' + ind_time1 + '.' + '\n' + '\n' + t + '\n' + t1
                sender_address = 'cse.takeoff@gmail.com'
                sender_pass = 'Takeoff@123'
                receiver_address = remail
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'Commerce Bank'
                message.attach(MIMEText(mail_content, 'plain'))
                ses = smtplib.SMTP('smtp.gmail.com', 587)
                ses.starttls()
                ses.login(sender_address, sender_pass)
                text = message.as_string()
                ses.sendmail(sender_address, receiver_address, text)
                ses.quit()
                flash("Transaction completed","success")
                return render_template("trans.html")
            else:
                flash("Account holder Email not found","info")
                return render_template("trans.html")
        else:
            flash("Account Number not found", "info")
            return render_template("trans.html")
        # else:
        #     msg = 'Thanks for choosing online Banking.'
        #     otp = "Please make a transaction on early hours i.e., During Bank working hours."
        #
        #     t = 'Regards,'
        #     t1 = 'Online Bank Service.'
        #     mail_content = msg + '\n' + otp + '\n' + '\n' + t + '\n' + t1
        #     sender_address = 'cse.takeoff@gmail.com'
        #     sender_pass = 'Takeoff@123'
        #     receiver_address = email
        #     message = MIMEMultipart()
        #     message['From'] = sender_address
        #     message['To'] = receiver_address
        #     message['Subject'] = 'E- Commerce Bank'
        #
        #     message.attach(MIMEText(mail_content, 'plain'))
        #     ses = smtplib.SMTP('smtp.gmail.com', 587)
        #     ses.starttls()
        #     ses.login(sender_address, sender_pass)
        #     text = message.as_string()
        #     ses.sendmail(sender_address, receiver_address, text)
        #     ses.quit()
        #     flash("")

    return render_template('trans.html')
@app.route('/history')
def history():
    email=session.get('email')
    sql="select * from transactions where semail='%s' ORDER BY date1 ASC "%(email)
    x=pd.read_sql_query(sql,db)
    x=x.drop(['id','saccno','semail','remail','swift','time1'], axis=1)
    return render_template('history.html',row_val=x.values.tolist())
@app.route('/forget')
def forget():
    return render_template('forget.html')

@app.route('/forgetback',methods=['POST', 'GET'])
def forgetback():
    if request.method == "POST":

        email = request.form['email']
        cpwd = request.form['cpwd']
        pwd = request.form['pwd']
        if pwd == cpwd:
            sq1 = "update registration set password='%s' where email='%s'" % (pwd, email)
            cur.execute(sq1, db)
            db.commit()
            msg = 'Your Email Id password is successfully changed. Now you can login. '
            t = 'Regards,'
            t1 = 'Online Bank Service.'
            mail_content = msg  + '\n' + '\n' + t + '\n' + t1
            sender_address = 'cse.takeoff@gmail.com'
            sender_pass = 'Takeoff@123'
            receiver_address = email
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = 'Commerce Bank'
            message.attach(MIMEText(mail_content, 'plain'))
            ses = smtplib.SMTP('smtp.gmail.com', 587)
            ses.starttls()
            ses.login(sender_address, sender_pass)
            text = message.as_string()
            ses.sendmail(sender_address, receiver_address, text)
            ses.quit()
            flash("Sucessfully password reset ", "success")
            return render_template("forget.html")
        else:
            flash("Password and Confirm password mismatches so please try again ", "success")
            return render_template("forget.html")

    return render_template('forget.html')

@app.route('/down')
def down():
    email=session.get('email')
    sql="select rname,raccno,ctg,transtype,amount,date1 from transactions where semail='%s' ORDER BY date1 ASC "%(email)
    x=pd.read_sql_query(sql,db)
    # x=x.drop(['id','saccno','semail','remail','swift','time1'], axis=1)
    # data=x.to_csv('CSV_Files/Data.csv')
    # data = pd.read_csv('CSV_Files/Data.csv')
    # # print(data)
    # data['Reciever Name'] = data.rname
    # data['Reciever Accno'] = data.raccno
    # data['Category'] = data.ctg
    # data['Transaction Type'] = data.transtype
    # data['Amount'] = data.amount
    # data['Date & Time'] = data.date1
    # data.drop(['Unnamed: 0','rname','raccno','ctg','transtype','amount','date1'],axis = 1,inplace = True)
    # print(data.columns)
    data=x.to_csv()
    print(data)
    # return render_template('down.html',cal_name=data.columns.values, row_val=data.values.tolist())
    return render_template('down.html',msg=data)

if __name__=='__main__':
    app.run(debug=True)
