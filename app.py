import json
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import sympy as sp

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return "FormuLister Solver API"

@app.route('/solve', methods=['POST'])
def solve():
    # Grab the body of the request
    req_body = json.loads(request.data)  
    equation_str = req_body['data']
    
    # Parse the inputted string to isolate the expression containing the variable
    expr_str = equation_str.split('=')
    x = sp.symbols('x')

    s1 = sp.sympify(expr_str[0])
    s2 = sp.sympify(expr_str[1])

    # Prepare the equation
    eq = sp.Eq(s1, s2)
    sol = sp.solve(eq, x)
    
    # Check if its only one out
    if len(sol) == 1:                
        # Make the response one item only if the output has only one item        
        response = make_response(jsonify({'result': str(sol[0])}))
    else:
        # Make the response a list if theres multiple items in the output
        response = make_response(jsonify({'result': str(sol)}))
    
    response.headers['Content-Type'] = 'application/json'
    
    return response

app.run()
