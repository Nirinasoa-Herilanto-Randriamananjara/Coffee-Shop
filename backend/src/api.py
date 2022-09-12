import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def retrieve_drinks():
    all_drinks = Drink.query.all()
    
    data = [drink.short() for drink in all_drinks]
    
    if len(data) == 0:
        abort(404)
    
    return jsonify({
        "success": True,
        "drinks": data
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(payload):
    all_drinks = Drink.query.all()
    
    data = [drink.long() for drink in all_drinks]

    if len(data) == 0:
        abort(404)
        
    return jsonify({
        "success": True,
        "drinks": data
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drinks(payload):
    try:
        body = request.get_json()
        
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        
        if recipe is None:
            abort(422)
        
        # recipe format required [{"name": "water", "color": "blue", "parts": 1}]
        recipe_drink = json.dumps(recipe)
        
        new_drink = Drink(title=title, recipe=recipe_drink)
        
        new_drink.insert()
        
        return jsonify({
            "success": True,
            "drinks": new_drink.long()
        })
        
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.get(drink_id)
        
        if drink is None:
            abort(404)
            
        update_title = body.get('title', None)
        update_recipe = body.get('recipe', None)
        
        if 'title' in body:
            drink.title = update_title
    
        if 'recipe' in body and update_recipe is not None:
            drink.recipe = json.dumps(update_recipe)
    
        drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
        
    except:
        abort(400)

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drink(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        
        if drink is None:
            abort(404)
            
        drink.delete()
        
        return jsonify({
            "success": True,
            "delete": drink.id
        })
        
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
    
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
    
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403
    
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
    
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405
    
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

'''
    AuthError handler
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description')
    }), error.status_code