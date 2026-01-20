from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Vulnerable Application</h1><p>This is a test application with known vulnerabilities.</p>"

@app.route('/search')
def search():
    query = request.args.get('q','')
    return f"Search Results for: {query}"

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    return f"Trying to login: {username}"

if __name__ == '__main__':
    app.run(port=5000)