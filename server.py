from flask import Flask, render_template, url_for, request, \
    redirect, flash, jsonify, abort
app = Flask(__name__)

from database_setup import Base, Item, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#import the session feature of flask as login_session
from flask import session as login_session
import random, string

#stuff for oauth third party authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask_login import LoginManager, login_user, login_required, logout_user
import json
from flask import make_response
import requests


#Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#setting up flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'showLogin'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

@login_manager.user_loader
def load_user(user_id):
    user = session.query(User).filter_by(id = user_id).first()
    return user

@app.route('/')
def frontPage():
    latest_items = session.query(Item).order_by(Item.time_created.desc()).limit(5)
    return render_template('front_page.html', latest_items = latest_items)

@app.route('/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'GET':
        return render_template('new_item.html')
    if request.method == 'POST':
        newItem = Item(name = request.form['name'], description = request.form['item-description'], category = request.form['category'], user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('new item created!')
        return redirect(url_for('frontPage'))

#routes for all the categories
@app.route('/<category_name>')
def categoryPage(category_name):
    category_name = str(category_name)
    category_items = session.query(Item).filter_by(category = category_name).all()
    return render_template('category_page.html', category_name=category_name, category_items = category_items)

#routes for items
@app.route('/<category>/<item_id>')
def itemPage(category, item_id):
    item = session.query(Item).filter_by(id = item_id).first()
    return render_template('item_page.html', category = category, item = item)

#edit and delete items
@app.route('/<category>/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(category, item_id):
    item = session.query(Item).filter_by(id = item_id).first()
    item_creator = item.user_id
    item_name = item.name
    item_description = item.description
    if int(login_session['user_id']) == item_creator:
        if request.method == 'GET':
            return render_template('edit_item.html', category = category, item_id = item_id, item_name = item_name, item_description = item_description)
        if request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['item-description']
            item.category = request.form['category']
            session.commit()
            return redirect(url_for('itemPage', category = category, item_id = item_id))
    else:
        abort(401)

@app.route('/<category>/<item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(category, item_id):
    item = session.query(Item).filter_by(id = item_id).first()
    session.delete(item)
    session.commit()
    return redirect(url_for('frontPage'))



#login
@app.route('/login')
def showLogin():
    next = request.referrer
    print next
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('/login.html', STATE=state, next=next)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    flow = flow_from_clientsecrets(
    'client_secrets.json',
    scope='https://www.googleapis.com/auth/drive.metadata.readonly')
    state = request.args.get('state')
    if login_session['state'] != request.args.get('state'):
        abort(400)
        print "state mismatch!"
    if request.args.get('error'):
        print "access denied", request.args.get('error')
        abort(400)
    auth_code = request.data
    print auth_code
    #flow requires a redirect_uri even though it's not used
    flow.redirect_uri = 'postmessage'
    credentials = flow.step2_exchange(auth_code)
    login_session['credentials'] = credentials.to_json()

    #get user info
    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(url, params=params)
    data = answer.json()

    user = getUser(data['email'])
    if not user:
        user = createUser(data)

    login_session['user_id'] = user.id
    #login user for flask-login
    login_user(user)

    return "success!"


@app.route('/gdisconnect')
@login_required
def gdisconnect():
    if login_session['credentials']:
        del login_session['credentials']
        del login_session['user_id']
        logout_user()
        return redirect(url_for('frontPage'))
    else:
        return make_response(json.dumps('Current user not connected.'))

    # access_token = login_session['access_token']
    # print login_session['username']
    # if access_token is None:
 # 	print 'Access Token is None'
    # 	response = make_response(json.dumps('Current user not connected.'), 401)
    # 	response.headers['Content-Type'] = 'application/json'
    # 	return response
    # url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    # h = httplib2.Http()
    # result = h.request(url, 'GET')[0]
    # print 'result is '
    # print result
    # if result['status'] == '200':
	# del login_session['access_token']
    # 	# del login_session['gplus_id']
    # 	del login_session['username']
    # 	del login_session['email']
    # 	response = make_response(json.dumps('Successfully disconnected.'), 200)
    # 	response.headers['Content-Type'] = 'application/json'
    # 	return response
    # else:
    # 	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    # 	response.headers['Content-Type'] = 'application/json'
    # 	return response

#API endpoint
@app.route('/<category>/<item_id>/JSON')
def itemJSON(category, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Item=item.serialize)

#local permission system helper functions
def createUser(data):
    newUser = User(name = data['username'], email = data['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = data['email']).one()
    return user

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUser(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user
    except:
        return None




if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
