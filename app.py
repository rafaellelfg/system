from flask import Flask

from routes import route 

app = Flask(__name__)
app.secret_key = "secret"

route(app)


# ==========================================
# BLOCK 3: Entry point
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)