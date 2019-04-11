from flask import Flask,render_template,request,url_for,redirect,session                           
import json

app = Flask(__name__)   

@app.route('/')                                   
def index():                                
    return render_template("index.html")                       
@app.route('/add_user')
def add_user():
    return "Hello World!"  
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
   
        
        return request.form["email"] + " " +request.form["passward"] 

    else:
        return render_template("login.html")

if __name__ == '__main__':                        
    app.run(host="0.0.0.0", port=80, debug=True)
    