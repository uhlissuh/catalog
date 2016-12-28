from flask import Flask, render_template
app = Flask(__name__)



@app.route('/')
def FrontPage():
    return render_template('front_page.html')




















if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
