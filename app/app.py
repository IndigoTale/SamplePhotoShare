from flask import Flask,render_template                           
import json

app = Flask(__name__)   

@app.route('/')                                   
def hello_world():                                
    return render_template("index.html")                       
@app.route('/add_user')
def add_user():
    return "Hello World!"  

if __name__ == '__main__':                        
    app.run(host="0.0.0.0", port=80, debug=True)
    