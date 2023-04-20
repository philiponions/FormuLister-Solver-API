import json
from flask import Flask, request, jsonify, make_response
import sympy as sp

app = Flask(__name__)


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

    eq = sp.Eq(s1, s2)
    sol = str(sp.solve(eq, x))    
        
    response = make_response(jsonify(sol))
    response.headers['Content-Type'] = 'application/json'
    return response

app.run()
