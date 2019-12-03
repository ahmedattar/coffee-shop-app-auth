import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# uncomment next line to drop all records and start db from scratch
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():

    # get all drinks
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .short()
    drinks_short = [drink.short() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # get all drinks and format using .long()
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .long()
    drinks_long = [drink.long() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_long
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    # get the drink info from request
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    # create a new drink
    drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
        # add drink to the database
        drink.insert()
    except Exception as e:
        print('ERROR: ', str(e))
        abort(422)

    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink_by_id(*args, **kwargs):
    # get id from kwargs
    id = kwargs['id']

    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # if drink not found
    if drink is None:
        abort(404)

    # get request body
    body = request.get_json()

    # update title if present in body
    if 'title' in body:
        print('TITLE: ', body['title'])
        print('TITLE TYPE: ', type(body['title']))
        drink.title = body['title']

    # update recipe if present in body
    if 'recipe' in body:
        print('RECIPE: ', body['recipe'])
        print('RECIPE TYPE: ', type(body['recipe']))
        drink.recipe = json.dumps(body['recipe'])

    print('UPDATED DRINK: ', drink.long())

    try:
        # update drink in database
        drink.insert()
    except Exception as e:
        # catch exceptions
        print('EXCEPTION: ', str(e))

        # Bad Request
        abort(400)

    # array containing .long() representation
    drink = [drink.long()]

    # return drink to view
    return jsonify({
        'success': True,
        'drinks': drink
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
    # get id from kwargs
    id = kwargs['id']

    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # if drink not found
    if drink is None:
        abort(404)

    try:
        # delete drink from database
        drink.delete()
    except Exception as e:
        # catch exceptions
        print('EXCEPTION: ', str(e))

        # server error
        abort(500)

    # return status and deleted drink id
    return jsonify({
        'success': True,
        'delete': id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
