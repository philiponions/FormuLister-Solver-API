import json
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
import sympy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt    
import io              

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return "FormuLister Solver API"

@app.route("/render", methods=['POST'])
def render():                     
    """Renders a formula. This takes in a request body and parses the equation
    with sympy. Sympy converts the equation to latex where it gets plotted with matplotlib."""

    # Grab the body of the request
    req_body = json.loads(request.data)  
    equation_str = req_body['data']
    # Parse the inputted string to isolate the expression containing the variable
    expr_str = equation_str.split('=')

    s1 = sp.sympify(expr_str[0])
    s2 = sp.sympify(expr_str[1])

    eq = sp.Eq(s1, s2)

    lat = sp.latex(eq)                                                                                                                

    ax = plt.subplot()

    # Build a rectangle in axes coords
    left, width = 0, 1
    bottom, height = 0, 1
    right = left + width
    top = bottom + height

    ax.text(0.5 * (left + right), 0.5 * (bottom + top), r"$%s$" % lat,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize = 50,
            transform=ax.transAxes)

    ax.set_axis_off()     
    
    # We dont wanna save the image to the server, so save it in a buffer
    buffer = io.BytesIO()
    ax.set_frame_on(False)  
    plt.savefig(buffer,  bbox_inches='tight',pad_inches = 0, dpi = 50)                

    # Send the file to the client as a response
    response = send_file(buffer, mimetype='image/png')

    # Clear buffer
    buffer.seek(0)    
    plt.clf()

    return response


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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
