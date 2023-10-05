from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from main import generate, transcribe
import os
import awsgi
# Create a Flask application
app = Flask(__name__)
#CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

# Define a route for "/api/hello" that returns "Hello, World!"
@app.route('/api/hello')
def hello():
    return 'Hello, World!'

@app.route('/api/generate', methods=['POST'])
def custom():
    try:
        # Get JSON data from the request
        data = request.get_json()

        print(data)
        filepath = os.path.join('uploads', data["filename"])
        if 'prompt' in data and data["filename"]:
            param_value = data['prompt']
            result = generate(param_value, filepath)
            return jsonify({"result": result})
        else:
            return jsonify({"error": "Missing 'prompt' in JSON request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Check if a file is present in the request
    if 'audioFile' not in request.files:
        return jsonify(error='No file part'), 400

    file = request.files['audioFile']

    # If no file is selected
    if file.filename == '':
        return jsonify(error='No selected file'), 400

    # Save and process the file
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    # Return a JSON response
    return jsonify(body='Uploaded successfully')
            
            
        
@app.route('/api/transcribe', methods=['POST'])
def handle_transcribe():
    # Get filename from request body
    filename = request.get_data(as_text=True)
    # Validate the filename
    if not filename:
        return jsonify(error="Filename is empty"), 400
    
    # Locate the file and transcribe
    try:
        filepath = os.path.join('uploads', filename)
        transcript = transcribe(f"{filepath}")  # Your existing transcription function
        print("transcipt: ", transcript) 
    except Exception as e:
        # Handle potential errors like FileNotFound or issues in the transcription function
        return jsonify(error=str(e)), 500
    
    # Return the transcription result
    return jsonify(result=transcript)

def lambda_handler(event, context):
    return awsgi.response(app, event, context)

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)

