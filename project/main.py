from flask import Flask,redirect,render_template,request,flash
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from datetime import date
from sqlalchemy import cast, Date,extract,func
from datetime import datetime, time

#my database connection
local_server=True
app=Flask(__name__)
app.secret_key="shrinidhi"


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/paintstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

# with open("config.json",'r') as c:
#     params=json.load(c)["params"]

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


class Test(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))

class Customer(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Fname=db.Column(db.String(20))
    Lname=db.Column(db.String(20))
    Email=db.Column(db.String(30),unique=True)
    Mobile=db.Column(db.String(13))
    Dob=db.Column(db.String(1000))

    def __init__(self,Fname,Lname,Email,Mobile,Dob):
        # self.id=user_id
        self.Fname=Fname
        self.Lname=Lname
        self.Email=Email
        self.Mobile=Mobile
        self.Dob=Dob
def get_customer_Fname(Email):
    customer = Customer.query.filter_by(Email=Email).first()
    return customer.Fname
def get_customer_Lname(Email):
    customer = Customer.query.filter_by(Email=Email).first()
    return customer.Lname

class Worker(UserMixin,db.Model):
    w_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    age=db.Column(db.String(3))
    gender=db.Column(db.String(6))
    mobile=db.Column(db.String(13))
    location=db.Column(db.String(20))
    address=db.Column(db.String(20))
    ret_id=db.Column(db.Integer,db.ForeignKey('retailer.ret_id'))

    def __init__(self,name,age,gender,mobile,location,address,ret_id):
        self.name=name
        self.age=age
        self.gender=gender
        self.mobile=mobile
        self.location=location
        self.address=address
        self.ret_id=ret_id

class Product(UserMixin,db.Model):
    pcode=db.Column(db.String(10),primary_key=True)
    paint_colour=db.Column(db.String(20))
    paint_type=db.Column(db.String(10))
    price=db.Column(db.String(10))
    quantity=db.Column(db.Integer)
    mfr_date=db.Column(db.String(20))
    exp_date=db.Column(db.String(20))
    

    def __init__(self,pcode,paint_colour,paint_type,price,quantity,mfr_date,exp_date):
        self.pcode=pcode
        self.paint_colour=paint_colour
        self.paint_type=paint_type
        self.price=price
        self.quantity=quantity
        self.mfr_date=mfr_date
        self.exp_date=exp_date

class Retailer(UserMixin,db.Model):
    ret_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20))
    password=db.Column(db.String(20))

class Inventory(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pcode=db.Column(db.String(10))
    paint_colour=db.Column(db.String(20))
    paint_type=db.Column(db.String(10))
    price=db.Column(db.String(10))
    quantity=db.Column(db.Integer)
    Action=db.Column(db.String(10))
    time_stamp=db.Column(db.String(20))

class Orders(db.Model):
    oid=db.Column(db.Integer,primary_key=True)
    cid=db.Column(db.Integer)
    rid=db.Column(db.Integer,db.ForeignKey('retailer.ret_id'))
    upiid=db.Column(db.String(50))
    pcode=db.Column(db.String(10))
    quantity=db.Column(db.Integer)
    total_amount=db.Column(db.Integer)
    name=db.Column(db.String(20))
    address=db.Column(db.String(100))
    pincode=db.Column(db.Integer)
    date=db.Column(db.String(20))
   

# routing of pages

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

@app.route("/retailerlogin")
def retailerlogin():
    return render_template("retailerlogin.html")

@app.route("/retailerhome")
def retailerhome():
    total_customers = Customer.query.count()
    today_date = date.today()
    order_count = Orders.query.filter(cast(Orders.date, Date) == today_date).count()
    total_customers = Customer.query.count()
    ofs = Product.query.filter(Product.quantity == 0).count()
    workeravailable= Worker.query.count()
    sum_amount = db.session.query(db.func.sum(Orders.total_amount)).filter(extract('day',Orders.date) == datetime.now().day,extract('month',Orders.date) == datetime.now().month,extract('year',Orders.date) == datetime.now().year).scalar()
    return render_template("retailer_home.html",tc=total_customers,oc=order_count,pc=sum_amount,ofs=ofs,work=workeravailable)

@app.route("/inventorylog")
def inventorylog():
    values=Inventory.query.all()
    return render_template("inventorylog.html",inven=values)

@app.route("/addworker")
def addworker():
    return render_template("worker/addworker.html")

@app.route("/delworker")
def delworker():
    all_data=Worker.query.all()
    return render_template("worker/delworker.html",workers=all_data)


@app.route("/viewworker")
def viewworker():
    all_data=Worker.query.all()
    return render_template("worker/viewworker.html",workers=all_data)

@app.route("/addpaint")
def addpaint():
    
    return render_template("paint/addpaint.html")

@app.route("/delpaint")
def delpaint():
    all_data=Product.query.all()
    return render_template("paint/delpaint.html",products=all_data)

@app.route("/updatepaint")
def updatepaint():
    al_data=Product.query.all()
    return render_template("paint/updatepaint.html",products=al_data)

@app.route("/viewpaint")
def viewpaint():
    all_data=Product.query.all()
    return render_template("paint/viewpaint.html",products=all_data)

@app.route("/addcust")
def addcust():
    return render_template("customer/addcust.html")

@app.route("/delcust")
def delcust():
    all_data=Customer.query.all()
    return render_template("customer/delcust.html",customers=all_data)

@app.route("/viewcust")
def viewcust():
    all_data=Customer.query.all()
    return render_template("customer/viewcust.html",customers=all_data)


# customer after login routings
@app.route("/intr_paint")
def intrpaint():
    
    results = Product.query.filter(Product.paint_type == 'interior').all()
    return render_template("aftrcustlogin/intrpaint.html",results=results)

@app.route("/extr_paint")
def extrpaint():
    
    results = Product.query.filter(Product.paint_type == 'exterior').all()
    return render_template("aftrcustlogin/extrpaint.html",results=results)

@app.route("/order")
def order():
    return render_template("aftrcustlogin/order.html")

@app.route("/wrkr")
def wrkr():
    
    all_data=Worker.query.all()
    return render_template("aftrcustlogin/wrkr.html",workers=all_data)

@app.route("/ordrhstry")
def ordrhstry():
    result = db.session.query(Orders, Product).filter(Orders.pcode == Product.pcode, Orders.cid == current_user.id).all()
    return render_template("aftrcustlogin/orderhistory.html",result=result)

@app.route("/retordrcv")
def retordrcv():
    result = Orders.query.join(Product, Orders.pcode == Product.pcode).join(Customer, Orders.cid == Customer.id).with_entities(Orders.oid, Product.paint_colour, Product.paint_type, Orders.quantity, Customer.Fname, Customer.Email, Orders.address, Orders.pincode, Customer.Mobile, Orders.date).order_by(Orders.date.desc(), Customer.Fname)

    db.session.remove()
    return render_template("ordrsrecived.html",result=result)


@app.route("/retpayrcv")
def retpayrcv():
    result = Orders.query.join(Product, Orders.pcode == Product.pcode).join(Customer, Orders.cid == Customer.id).with_entities(Orders.oid,Customer.Fname,Customer.Email, Orders.upiid, Orders.name, Orders.total_amount, Orders.date).order_by(Orders.date.desc())

    return render_template("payrcvd.html",result=result)



@app.route("/viewprof")
def viewprof(): 
    return render_template("aftrcustlogin/viewprofile.html")

@app.route("/hmebttn")
def hmbttn():
    return render_template("aftrcustlogin/cust_home.html")

@app.route("/currentorder")
def currentorder():
    today = datetime.now().date()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    orders = Orders.query.filter(Orders.date.between(start_of_day, end_of_day)).all()
    return render_template("aftrcustlogin/pendingorder.html",result=orders)

@app.route("/todaypayment")
def todaypayment():
    today = datetime.now().date()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    orders = Orders.query.filter(Orders.date.between(start_of_day, end_of_day)).all()
    return render_template("aftrcustlogin/todaypayment.html",result=orders)

@app.route("/outofstock")
def oos():
    producto = Product.query.filter_by(quantity=0).all()
    return render_template("aftrcustlogin/outofstock.html",products=producto)



@app.route("/buy_intr_paint",methods=['GET','POST'])
def buyintrpaint():
    results = Product.query.filter(Product.paint_type == 'interior').all()
    return render_template("aftrcustlogin/buyintrpaint.html",results=results)

@app.route("/buy_extr_paint",methods=['GET','POST'])
def buyextrpaint():
    results = Product.query.filter(Product.paint_type == 'exterior').all()
    return render_template("aftrcustlogin/buyextrpaint.html",results=results)


@app.route("/custhome")
def custhome():
    results = Product.query.filter(Product.paint_type == 'exterior', Product.quantity > 0).count()
    intravai=Product.query.filter(Product.paint_type == 'interior', Product.quantity > 0).count()
    workeravai=Worker.query.count()
    totalexpenditure=db.session.query(func.sum(Orders.total_amount)).filter(Orders.cid == current_user.id).scalar()
    numberoforders= db.session.query(func.sum(Orders.quantity)).filter(Orders.cid == current_user.id).scalar()
    return render_template("aftrcustlogin/cust_home.html",extr=results,woe=workeravai,intr=intravai,te=totalexpenditure,no=numberoforders)
# checkout code------------------

@app.route("/buyextr/<pcode>/",methods=['GET','POST'])
def checkoutextr(pcode): 
    product = Product.query.filter_by(pcode=pcode).first()
    if product.quantity==0: 
        flash('Selected product is currently out of stock!!!')
        return redirect(url_for('buyextrpaint'))

    return render_template("aftrcustlogin/checkoutextr.html",checkedpaint=product)

@app.route("/ordersuccessextr",methods=['GET','POST'])
def ordr_scs_extr():
    if request.method=="POST":
        pcode1=request.form.get('pcode')
        pur_qty=request.form.get('qty')

        upiname=request.form.get('upiname')
        total_amt=request.form.get('tamt')
        upi=request.form.get('cardnumbr')
        cid=request.form.get('cid')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        # flash('order placed'+pcode1+pur_qty+upiname+total_amt+cid+address+pincode)
        # flash(upi)
        Session = sessionmaker(bind=db.engine)
        session = Session()
        new_user = Orders(cid=cid,rid='1',upiid=upi,pcode=pcode1,quantity=pur_qty,total_amount=total_amt,name=upiname,address=address,pincode=pincode)
        session.add(new_user)
        session.commit()  


        product = Product.query.filter_by(pcode=pcode1).first()
        if product.quantity!=0:
            product.quantity -= int(pur_qty)
            db.session.commit()
            flash('Last order Successfull')
 
    return redirect(url_for('buyextrpaint'))

# ------------------------------------------------------------------------------


@app.route("/buyint/<pcode>/",methods=['GET','POST'])
def checkoutintr(pcode):   
    product = Product.query.filter_by(pcode=pcode).first()
    if product.quantity==0: 
        flash('Selected product is currently out of stock!!!')
        return redirect(url_for('buyintrpaint'))  
    return render_template("aftrcustlogin/checkoutintr.html",checkedpaint=product)

@app.route("/ordersuccessintr",methods=['GET','POST'])
def ordr_scs_intr():
    if request.method=="POST":
        pcode1=request.form.get('pcode')
        pur_qty=request.form.get('qty')

        upiname=request.form.get('upiname')
        total_amt=request.form.get('tamt')
        upi=request.form.get('cardnumbr')
        cid=request.form.get('cid')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        
        Session = sessionmaker(bind=db.engine)
        session = Session()
        new_user = Orders(cid=cid,rid='1',upiid=upi,pcode=pcode1,quantity=pur_qty,total_amount=total_amt,name=upiname,address=address,pincode=pincode)
        session.add(new_user)
        session.commit()  
          
          
        product = Product.query.filter_by(pcode=pcode1).first()
        if product.quantity!=0:
            product.quantity -= int(pur_qty)
            db.session.commit()
            flash('Last order Successfull')
    return redirect(url_for('buyintrpaint'))




# delete data route
@app.route("/delworkerdata/<w_id>/",methods=['GET','POST'])
def delworkerdata(w_id):   
    my_data=Worker.query.get(w_id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Worker Deleted Sucessfully")
    return redirect(url_for('delworker'))


@app.route("/delpaintdata/<pcode>/",methods=['GET','POST'])
def delpaintdata(pcode):   
    my_data=Product.query.get(pcode)
    db.session.delete(my_data)
    db.session.commit()
    flash("Paint Deleted Sucessfully")
    return redirect(url_for('delpaint'))

@app.route("/delcustdata/<id>/",methods=['GET','POST'])
def delcustdata(id):   
    my_data=Customer.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Customer Deleted Sucessfully")
    return redirect(url_for('delcust'))

@app.route("/updtpint",methods=['GET','POST'])
def updtpint():   
    if request.method=="POST":
        pcode=request.form.get('pcode')
        my_data=Product.query.get(pcode)
        if my_data is None:
            flash("Product with code " + pcode + " not found.")
        else:
            pc=request.form.get('Paintcolour')
            if pc != "":
                my_data.paint_colour=pc

            pr=request.form.get('Price')
            if pr != "":
                my_data.price=pr

            qty=request.form.get('Quantity')
            if qty != "":
                 my_data.quantity=qty
            db.session.commit()
            flash("Row [ pcode = "+ pcode +" ] Updated Sucessfully")
    return redirect(url_for('updatepaint'))


@app.route("/updateworker",methods=['GET','POST'])
def updateworker():
    all_data=Worker.query.all()
    if request.method=="POST":
        wid=request.form.get('id')
        my_dat=Worker.query.get(wid)
        # flash("Row [ Name = "+ name +" ] Updated Sucessfully")
        if my_dat is None:
            flash("Worker with name " + nm + " not found.")
        else:
            pc=request.form.get('age')
            if pc != "":
                my_dat.age=pc
            pr=request.form.get('location')
            if pr != "":
                my_dat.location=pr
            qty=request.form.get('address')
            if qty != "":
                my_dat.address=qty
            nm=request.form.get('name')
            if nm != "":
                my_dat.name=nm
            gn=request.form.get('gender')
            if gn != "":
                my_dat.gender=gn
            db.session.commit()
            flash("Row with  Worker_id="+ wid +"  Updated Sucessfully")
    
    return render_template("worker/updateworker.html",workers=all_data)



# for signup database connection
@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method=="POST":
        Fname=request.form.get("first_name")
        Lname=request.form.get('last_name')
        Email=request.form.get('email')
        Mobile=request.form.get('phone')
        Dob=request.form.get('date_b')
        encpassword=generate_password_hash(Dob)
        # cheks if user exist during signup
        user=Customer.query.filter_by(Email=Email).first()
        if user:
            flash("Email already exists!....Please Login")
            return render_template("usersignup.html")
        Session = sessionmaker(bind=db.engine)
        session = Session()
        new_user = Customer(Fname=Fname, Lname=Lname, Email=Email, Mobile=Mobile, Dob=encpassword)
        session.add(new_user)
        session.commit()      
         # new_user=db.engine.execute(f"INSERT INTO `customer` (`Fname`,`Lname`,`Email`,`Mobile`,`Dob`) VALUES ('{Fname}','{Lname},'{Email}','{Mobile}','{encpassword}')")
    #    login directly fter signup
        flash('Sign in sucessfull....Please LOGIN')
        return render_template("usersignup.html")      
    return render_template("usersignup.html")



# for cust login databse connection
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        Email=request.form.get('email')
        Dob=request.form.get('date_b')
        user=Customer.query.filter_by(Email=Email).first()
        
        if user and check_password_hash(user.Dob,Dob):
            login_user(user)
            flash('You were successfully logged in')
            userfnme=get_customer_Fname(Email)
            userlnme=get_customer_Lname(Email)
            results = Product.query.filter(Product.paint_type == 'exterior', Product.quantity > 0).count()
            intravai=Product.query.filter(Product.paint_type == 'interior', Product.quantity > 0).count()
            workeravai=Worker.query.count()
            totalexpenditure=db.session.query(func.sum(Orders.total_amount)).filter(Orders.cid == current_user.id).scalar()
            numberoforders= db.session.query(func.sum(Orders.quantity)).filter(Orders.cid == current_user.id).scalar()
            return render_template("aftrcustlogin/cust_home.html",currentuserfname=userfnme,currentuserlname=userlnme,extr=results,woe=workeravai,intr=intravai,te=totalexpenditure,no=numberoforders)
                      
        else:
            flash('Invalid Credentials')
            # return 'login failed'          
            # return render_template("usersignup.html")    
    return render_template("usersignup.html")


# logout
@app.route("/logout") 
@login_required
def logout():
    logout_user()
    flash("Logout sucessfull")
    return redirect(url_for('usersignup'))


# /for ret login
@app.route("/retlogin",methods=["POST","GET"])
def retlogin():
    if request.method=="POST":
        usernam=request.form.get('username')
        password=request.form.get('password')
        if (usernam=='admin' and password=='admin'):           
            # user2=retailer.query.filter_by(username=usernam).first()
            # login_user(user2)
            total_customers = Customer.query.count()
            today_date = date.today()
            order_count = Orders.query.filter(cast(Orders.date, Date) == today_date).count()
            total_customers = Customer.query.count()
            workeravailable= Worker.query.count()
            sum_amount = db.session.query(db.func.sum(Orders.total_amount)).filter(extract('day',Orders.date) == datetime.now().day,extract('month',Orders.date) == datetime.now().month,extract('year',Orders.date) == datetime.now().year).scalar()
            ofs = Product.query.filter(Product.quantity == 0).count()
            return render_template("retailer_home.html",tc=total_customers,oc=order_count,pc=sum_amount,ofs=ofs,work=workeravailable)
        else:
            flash("Invalid Credentials")
            # return 'login fail'                     
            # return render_template("usersignup.html")    
    return render_template("retailerlogin.html")



# worker add
@app.route("/getworker",methods=["POST","GET"])
def adworker():
    if request.method=="POST":
        name=request.form.get("name")
        age=request.form.get('age')
        gender=request.form.get('gender')
        location=request.form.get('location')
        mobile=request.form.get('phone')
        address=request.form.get('address')
        name1=Worker.query.filter_by(name=name).first()
        location1=Worker.query.filter_by(location=location).first()
        age1=Worker.query.filter_by(age=age).first()
        if name1 and location1 and age1:
            flash("Worker already exists!")
            return render_template("worker/addworker.html")
        Session = sessionmaker(bind=db.engine)
        session = Session()
        new_user = Worker(name=name, age=age, gender=gender, mobile=mobile, location=location, address=address,ret_id='1')
        session.add(new_user)
        session.commit() 
        flash('Worker added sucessfully')
        return render_template("worker/addworker.html")
    return render_template("retailer_home.html")     
   

# paint add
@app.route("/getpaint",methods=["POST","GET"])
def adpaint():
    if request.method=="POST":
        pcode=request.form.get("paintcode")
        pclr=request.form.get('paintcolour')
        ptype=request.form.get('ptype')
        price=request.form.get('price')
        quantity=request.form.get('quantity')
        mfd=request.form.get('mfd')
        exp=request.form.get('exp')
        pcode1=Product.query.filter_by(pcode=pcode).first()    
        if pcode1:
            flash("Paint already exists! and quantity updated")
            
            my_data = Product.query.filter_by(pcode=pcode).first()
            x = my_data.quantity
            my_data.quantity=x+int(quantity)
            db.session.commit()

            return render_template("paint/addpaint.html")
        Session = sessionmaker(bind=db.engine)
        session = Session()
        new_user = Product(pcode=pcode, paint_colour=pclr, paint_type=ptype, price=price, quantity=quantity,mfr_date=mfd,exp_date=exp)
        session.add(new_user)
        session.commit()
        flash('Paint added sucessfully')
        return render_template("paint/addpaint.html")
    return render_template("retailer_home.html") 


# for  customer add
@app.route("/custadd",methods=["POST","GET"])
def custadd():
    if request.method=="POST":
        Fname=request.form.get("first_name")
        Lname=request.form.get('last_name')
        Email=request.form.get('email')
        Mobile=request.form.get('phone')
        Dob=request.form.get('date_b')
        encpassword=generate_password_hash(Dob)
        # cheks if user exist during signup
        user=Customer.query.filter_by(Email=Email).first()
        if user:
            flash("Customer already exists!....")
            return render_template("addcust.html")
        Session = sessionmaker(bind=db.engine)
        session = Session()
        new_user = Customer(Fname=Fname, Lname=Lname, Email=Email, Mobile=Mobile, Dob=encpassword)
        session.add(new_user)
        session.commit()      
         # new_user=db.engine.execute(f"INSERT INTO `customer` (`Fname`,`Lname`,`Email`,`Mobile`,`Dob`) VALUES ('{Fname}','{Lname},'{Email}','{Mobile}','{encpassword}')")
    #    login directly fter signup
        flash('Customer added sucessfully')
        return render_template("retailer_home.html")
    return render_template("addcust.html")      
    

# paint add
@app.route("/gtpaint",methods=["POST","GET"])
def addpaints():
    if request.method=="POST":
        pcode1=request.form.get("paintcode")
        pclr=request.form.get('paintcolour')
        ptype=request.form.get('ptype')
        price=request.form.get('price')
        quantity=request.form.get('quantity')
        mfd=request.form.get('mfd')
        exp=request.form.get('exp')

        stmt = text("CALL insert_or_update_product(:pcode1, :paint_colour, :paint_type, :price, :quantity, :mfr_date, :exp_date)")
        params = {'pcode1': pcode1, 'paint_colour': pclr, 'paint_type': ptype, 'price': price, 'quantity': quantity, 'mfr_date': mfd, 'exp_date': exp}
        db.engine.execute(stmt, params)
       
        # CREATE TRIGGER `productinserted` AFTER INSERT ON `product` FOR EACH ROW INSERT INTO inventory VALUES(null,NEW.pcode,NEW.paint_colour,NEW.paint_type,NEW.price,NEW.quantity,'INSERTED',NOW()); 
        #db.engine.execute("CREATE TRIGGER `productinserted` AFTER INSERT ON `product` FOR EACH ROW INSERT INTO inventory VALUES(null,NEW.pcode,NEW.paint_colour,NEW.paint_type,NEW.price,NEW.quantity,'INSERTED',NOW());")    
        flash('Paint added sucessfully')
        return render_template("paint/addpaint.html")
    return render_template("retailer_home.html") 






# calculator
@app.route("/budgetcalculator", methods=["GET", "POST"])
def budgetcalculator():
    products=Product.query.all()
    if request.method == "POST":
        pcode = request.form.get("pcode")
        parea = float(request.form.get("coverage"))
        ncoat = float(request.form.get("coats"))
        my_data = Product.query.filter_by(pcode=pcode).first()
        if my_data:
            x = int(my_data.price)
            paint_budget = calculate_paint_budget(parea, ncoat, x)
            return render_template("budgetcalculator.html", result=paint_budget,products=products)
    return render_template("budgetcalculator.html",products=products)




def calculate_paint_budget(parea, ncoat, x):
    paint_needed = parea * ncoat * x
    return paint_needed
#testing db connected or not
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return 'My databae conncted'      
    except Exception as e:
        print(e)
        return f'My databae not conncted{e}'

# Create a quantity cal to the database
@app.route("/paintcalculator",methods=["POST","GET"])
def paintcalculator():
    if request.method=="POST":
        square = float(request.form.get('square-feet'))
        pcover = float(request.form.get('coverage'))
        coats = float(request.form.get('coats'))
        paint_quantity = calculate_paint_quantity(square, pcover, coats)
        return render_template("paintcalculator.html",result=paint_quantity)
    return render_template("paintcalculator.html")  

# Function to calculate the amount of paint needed for a room
def calculate_paint_quantity(square ,pcover, coats):
    paint_required= square / pcover
    paint_needed=paint_required * coats
    return paint_needed


app.run(debug=True)