from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "message": "Web Calculator API",
        "endpoints": {
            "add": "/add/<a>&<b>",
            "subtract": "/subtract/<a>&<b>",
            "multiply": "/multiply/<a>&<b>",
            "divide": "/divide/<a>&<b>",
            "health": "/health"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "web-calculator",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/add/<a>&<b>')
def add(a, b):
    try:
        result = float(a) + float(b)
        return jsonify({
            "operation": "add",
            "input": {"a": float(a), "b": float(b)},
            "result": result
        })
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400

@app.route('/subtract/<a>&<b>')
def subtract(a, b):
    try:
        result = float(a) - float(b)
        return jsonify({
            "operation": "subtract",
            "input": {"a": float(a), "b": float(b)},
            "result": result
        })
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400

@app.route('/multiply/<a>&<b>')
def multiply(a, b):
    try:
        result = float(a) * float(b)
        return jsonify({
            "operation": "multiply",
            "input": {"a": float(a), "b": float(b)},
            "result": result
        })
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400

@app.route('/divide/<a>&<b>')
def divide(a, b):
    try:
        if float(b) == 0:
            return jsonify({"error": "Division by zero"}), 400
        result = float(a) / float(b)
        return jsonify({
            "operation": "divide",
            "input": {"a": float(a), "b": float(b)},
            "result": result
        })
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)