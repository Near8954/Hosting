from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    param = {}
    param['username'] = "user"
    param['title'] = "Home page"
    return render_template('index.html', **param)


if __name__ == '__main__':
    app.run(debug=True)
