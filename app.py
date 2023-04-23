import json
from flask import Flask, request, jsonify, make_response, send_file, Response
from flask_cors import CORS
import sympy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt    
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import io              

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return "FormuLister Solver API"

def fig_response():
    """Turn a matplotlib Figure into Flask response"""
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = np.random.rand(100)
    ys = np.random.rand(100)
    axis.plot(xs, ys)
    output = io.BytesIO()
    FigureCanvas(plt).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/render", methods=['POST'])
def render():                   
    buffer = io.BytesIO()                                 
    # Grab the body of the request
    req_body = json.loads(request.data)  
    equation_str = req_body['data']
    # Parse the inputted string to isolate the expression containing the variable
    expr_str = equation_str.split('=')

    s1 = sp.sympify(expr_str[0])
    s2 = sp.sympify(expr_str[1])

    eq = sp.Eq(s1, s2)

    lat = sp.latex(eq)                                                            
                 
    left, width = .25, .5
    bottom, height = .25, .5                                           

    ax = plt.subplot()

    # Build a rectangle in axes coords
    left, width = .25, .5
    bottom, height = .25, .5
    right = left + width
    top = bottom + height
    p = plt.Rectangle((left, bottom), width, height, fill=False)
    p.set_transform(ax.transAxes)
    p.set_clip_on(False)
    ax.add_patch(p)


    ax.text(0.5 * (left + right), 0.5 * (bottom + top), r"$%s$" % lat,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize = 20,
            transform=ax.transAxes)

    ax.set_axis_off()     
    
    # We dont wanna save the image to the server, so save it in a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer)                

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

app.run()
