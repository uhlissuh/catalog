from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)

from database_setup import Base, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def FrontPage():
    return render_template('front_page.html')

@app.route('/item/new', methods=['GET', 'POST'])
def newItem():
    if request.method == 'GET':
        return render_template('new_item.html')
    if request.method == 'POST':
        newItem = Item()




















if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
