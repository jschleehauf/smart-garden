from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug = True

@app.route("/")         # This associates a path with a function
def hello():            # This function will run when the root URL is accessed
    return render_template('hello.html', message="Hello World!")

@app.route("/example")
def example():
    return "This is an example route"

if __name__ == "__main__":
  app.run(host='192.168.1.24', port=8080)
