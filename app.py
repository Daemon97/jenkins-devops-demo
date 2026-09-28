from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>Jenkins CI/CD Demo</title>
        </head>
        <body>
            <h1>Hello from Jenkins CI/CD!</h1>
            <h2>Version: 1.0</h2>
            <p>Environment: Production</p>
        </body>
    </html>
    """

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
