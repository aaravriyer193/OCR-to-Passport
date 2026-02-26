import os
import json
import base64
import requests
from flask import Flask, request, render_template_string, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Create a secret key for YOUR newly built API
# Put this in your .env file as well: MY_APP_API_KEY=super_secret_password_123
MY_APP_API_KEY = os.getenv("MY_APP_API_KEY") 

app = Flask(__name__)

# --- HTML FRONTEND TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Passport Data Extractor</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 2rem auto; padding: 1rem; color: #333; }
        .upload-area { border: 2px dashed #ccc; padding: 2rem; text-align: center; border-radius: 8px; margin-bottom: 1rem; background: #fafafa; }
        .btn { background: #007BFF; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
        .btn:hover { background: #0056b3; }
        #results { margin-top: 2rem; background: #f4f4f4; padding: 1.5rem; border-radius: 8px; display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: white; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #e9ecef; width: 40%; color: #333; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        #loading { display: none; margin-top: 1rem; color: #666; font-style: italic; text-align: center; }
    </style>
</head>
<body>
    <h2>Passport Data Extractor</h2>
    <div class="upload-area">
        <form id="uploadForm">
            <label for="imageInput"><strong>Select Passport Image:</strong></label><br><br>
            <input type="file" id="imageInput" name="image" accept=".png, .jpg, .jpeg, .webp" required>
            <br>
            <button type="submit" class="btn">Extract Data</button>
        </form>
    </div>
    
    <div id="loading">Sending image to Vision LLM... Please wait.</div>
    
    <div id="results">
        <h3>Extracted Information</h3>
        <div id="resultContent"></div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('imageInput');
            const file = fileInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('image', file);

            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';

            try {
                // Using the web UI route
                const response = await fetch('/web-extract', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    const contentDiv = document.getElementById('resultContent');
                    contentDiv.innerHTML = '';
                    
                    let extractedData;
                    try {
                        extractedData = typeof data.extracted_data === 'string' 
                            ? JSON.parse(data.extracted_data) 
                            : data.extracted_data;
                    } catch (parseErr) {
                        contentDiv.innerHTML = `<div style="color:red;">Error parsing LLM response. Raw output: ${data.extracted_data}</div>`;
                        document.getElementById('results').style.display = 'block';
                        return;
                    }

                    let tableHTML = '<table><tbody>';
                    for (const [key, value] of Object.entries(extractedData)) {
                        const formattedKey = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        tableHTML += `<tr><th>${formattedKey}</th><td>${value || 'Not found'}</td></tr>`;
                    }
                    tableHTML += '</tbody></table>';
                    contentDiv.innerHTML = tableHTML;
                    
                    document.getElementById('results').style.display = 'block';
                }
            } catch (err) {
                console.error(err);
                alert('An error occurred during extraction.');
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

# --- CORE EXTRACTION LOGIC ---
def process_passport_image(base64_image, mime_type):
    """Handles the communication with OpenRouter."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key is missing.")

    prompt = """
    You are a strict data extraction API. Your ONLY purpose is to extract information from the provided passport image and return a raw JSON object. And PLEASE DON'T THINK MUCH

    Extract the following information:
    - First Name
    - Last Name
    - Passport Number
    - Date of Birth
    - Date of Issue
    - Nationality 
    - place of passport issuance
    - middle name
    - gender
    - place of birth
    - issuing authority
    - Date of Expiry
    - Personal Number (if available)
    - Document Number (if available)

    CRITICAL INSTRUCTIONS:
    1. DO NOT describe the image.
    2. DO NOT include any conversational text, preamble, or explanations.
    3. DO NOT use markdown formatting (no ```json).
    4. Your entire response MUST start with '{' and end with '}'.
    
    Use exactly this JSON schema:
    {
        "first_name": "",
        "last_name": "",
        "Date of Birth": "",
        "Date of Issue": "",
        "Nationality": "",
        "place of passport issuance": "",
        "middle name": "",
        "gender": "male/female",
        "place of birth": "",
        "issuing authority": "",
        "Date of Expiry": "",
        "passport_number": "",
        "personal_number": "",
        "document_number": ""
    }
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen3.5-flash-02-23", # Using a highly capable free vision model
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                ]
            }
        ],
        "provider": {
        "order": ["alibaba"],
        "allow_fallbacks": False,
        "sort": "throughput"
        }

    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    
    llm_output = response.json()["choices"][0]["message"]["content"].strip()
    
    # Clean up any rogue markdown
    if llm_output.startswith("```json"): llm_output = llm_output[7:]
    if llm_output.startswith("```"): llm_output = llm_output[3:]
    if llm_output.endswith("```"): llm_output = llm_output[:-3]

    return llm_output.strip()

# --- ROUTES ---

@app.route('/', methods=['GET'])
def index():
    """Serves the HTML frontend."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/web-extract', methods=['POST'])
def web_extract():
    """Endpoint used by the HTML frontend."""
    if 'image' not in request.files or request.files['image'].filename == '':
        return jsonify({"error": "No image uploaded"}), 400

    try:
        file = request.files['image']
        base64_image = base64.b64encode(file.read()).decode('utf-8')
        mime_type = file.mimetype or 'image/jpeg'
        
        result = process_passport_image(base64_image, mime_type)
        return jsonify({"extracted_data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/extract', methods=['POST'])
def api_extract():
    """Dedicated API Endpoint for external applications."""
    
    # 1. Require an API key for your own app
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {MY_APP_API_KEY}":
        return jsonify({"error": "Unauthorized. Invalid or missing API key."}), 401

    try:
        # 2. Check if they sent a file (multipart/form-data)
        if 'image' in request.files:
            file = request.files['image']
            base64_image = base64.b64encode(file.read()).decode('utf-8')
            mime_type = file.mimetype or 'image/jpeg'
            
        # 3. Or check if they sent a JSON payload with a base64 string
        elif request.is_json and 'image_base64' in request.json:
            base64_image = request.json['image_base64']
            mime_type = request.json.get('mime_type', 'image/jpeg')
            
        else:
            return jsonify({"error": "Must provide 'image' file or JSON with 'image_base64'"}), 400

        # 4. Process and return the raw parsed JSON
        result_string = process_passport_image(base64_image, mime_type)
        return jsonify({
            "status": "success",
            "data": json.loads(result_string) # Parse it to ensure the API returns real JSON, not a string
        })

    except json.JSONDecodeError:
        return jsonify({"error": "LLM returned invalid JSON format", "raw_output": result_string}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")