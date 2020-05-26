from flask import Flask, request, jsonify
from backend import User
import jwt
from jwt.exceptions import DecodeError
from flask_cors import CORS
app = Flask(__name__)
# MongoDB
app.config['MONGO_DBNAME'] = 'restdb'  # TODO: use YAML to avoid hard coding
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'  # TODO: use YAML to avoid hard coding
user = User()
current_user = None
# CORS
app = Flask(__name__)
cors = CORS(app)


@app.route('/api/', methods=['GET'])
def get():
    args = dict(request.args)
    if '_id' in args:
        args['_id'] = int(args['_id'])
    return jsonify(user.get(args))


@app.route('/current_user/', methods=['GET'])
def get_current_user():
    global current_user
    if current_user is None:
        return {}
    else:
        return current_user


def __remove_password(user: dict) -> dict:
    user.pop('password')
    return user


@app.route('/api_id/', methods=['GET'])
def get_id():
    args = dict(request.args)
    return jsonify(user.get_id(int(args['_id'])))


@app.route('/decode/', methods=['POST'])
def decode():
    args = dict(request.args)
    results = {'loggedIn': False, 'messages': []}
    encoded = bytes(args['hash'].encode())
    global current_user
    try:
        current_user = jwt.decode(encoded, '', algorithms=['HS256'])
        results['messages'].append("Decoded.")
        results['loggedIn'] = True
        results['results'] = __remove_password(current_user)
    except DecodeError:
        results['messages'].append("Failed to decode.")
        results['loggedIn'] = False
        current_user = None
    return jsonify(results), 200


@app.route('/logout/', methods=['POST'])
def logout():
    global current_user
    current_user = None

@app.route('/login/', methods=['POST'])
def login():
    args = dict(request.args)
    results = {'loggedIn': False, 'messages': [], 'args': args, 'hash': None}
    is_successful = True
    global current_user
    if 'email' not in args:
        results['messages'].append("email not specified.")
        is_successful = False
    if 'password' not in args:
        results['messages'].append("password not specified.")
        is_successful = False
    if is_successful:
        if len(user.get({'email': args['email'], 'password': args['password'], })):
            docs = user.get({'email': args['email']})
            key = next(iter(docs))
            current_user = docs[key]
            results['hash'] = jwt.encode(current_user, '', algorithm='HS256').__str__()[2:-1]
            results['messages'] = 'successfully logged in.'
            results['results'] = __remove_password(current_user)
        else:
            current_user = None
            is_successful = False
            results['messages'].append("given combination of email and password does not exit.")
    results['loggedIn'] = is_successful
    return jsonify(results), 200


@app.route('/api/', methods=['POST'])
def create():
    args = dict(request.args)
    results = {'messages': [], 'args': args, 'results': []}
    doc = {}
    is_successful = True
    if 'email' in args:
        if len(user.get({'email': args['email']})):
            is_successful = False
            results['messages'].append("email is already taken.")
        else:
            doc['email'] = args['email']  # TODO: Might need verification
    else:
        results['messages'].append("email not specified.")
        is_successful = False
    if 'password' in args:
        doc['password'] = args['password']  # TODO: Might need verification
    else:
        results['messages'].append("password not specified.")
        is_successful = False
    if 'fname' in args:
        doc['fname'] = args['fname']
    else:
        results['messages'].append("fname not specified.")
        is_successful = False
    if 'lname' in args:
        doc['lname'] = args['lname']
    else:
        results['messages'].append("lname not specified.")
        is_successful = False
    if is_successful:
        try:
            results['results'] = user.create(doc)
            results['messages'] = 'Successfully write DB.'
        except:
            results['messages'] = 'Failed to write DB.'
    else:
        results['messages'].append("Did not write DB.")
    return results, 200


@app.route('/api/', methods=['PUT'])
def update():
    args = dict(request.args)
    if '_id' not in args:
        raise Exception('_id is not specified')
    _id = int(args.pop('_id'))
    user.update(_id, args)
    print('PUT', 'args', args)
    return args


@app.route('/api/', methods=['DELETE'])
def delete():
    args = dict(request.args)
    user.delete(int(args['_id']))
    return args


@app.route('/refresh_db/', methods=['DELETE'])
def refresh_db():
    user.refresh_db()
    return jsonify({'result': 'done'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run(debug=True)
