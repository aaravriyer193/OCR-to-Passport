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
MY_APP_API_KEY = os.getenv("MY_APP_API_KEY") 

app = Flask(__name__)

# --- HTML FRONTEND TEMPLATE (SCI-FI UI UPGRADE) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Passport Extractor </title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-cyan: #00f3ff;
            --neon-pink: #ff00ea;
            --bg-dark: #050b14;
            --card-glass: rgba(10, 16, 30, 0.85);
            --text-main: #e2e8f0;
            --text-muted: #8b9bb4;
            --grid-color: rgba(0, 243, 255, 0.05);
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            background-image: 
                linear-gradient(var(--grid-color) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
            background-size: 30px 30px;
            color: var(--text-main);
            min-height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }

        .container {
            background: var(--card-glass);
            width: 100%;
            max-width: 600px;
            border-radius: 12px;
            border: 1px solid rgba(0, 243, 255, 0.2);
            box-shadow: 0 0 30px rgba(0, 243, 255, 0.05), inset 0 0 20px rgba(0, 243, 255, 0.02);
            backdrop-filter: blur(10px);
            padding: 2.5rem;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
        }

        /* Sci-Fi glowing corners effect */
        .container::before, .container::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border: 2px solid var(--neon-cyan);
            pointer-events: none;
        }
        .container::before { top: 10px; left: 10px; border-right: none; border-bottom: none; }
        .container::after { bottom: 10px; right: 10px; border-left: none; border-top: none; }

        .header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .header h2 {
            margin: 0;
            font-family: 'Orbitron', sans-serif;
            font-size: 2rem;
            letter-spacing: 2px;
            color: var(--neon-cyan);
            text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
            text-transform: uppercase;
        }

        .header p {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 0.5rem;
            letter-spacing: 1px;
        }

        /* Custom File Upload Area */
        .upload-area {
            border: 1px dashed rgba(0, 243, 255, 0.4);
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: rgba(0, 243, 255, 0.02);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .upload-area:hover {
            border-color: var(--neon-cyan);
            background: rgba(0, 243, 255, 0.05);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.1) inset;
        }

        .upload-area input[type="file"] {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }

        .upload-icon {
            width: 48px;
            height: 48px;
            color: var(--neon-cyan);
            margin-bottom: 1rem;
            filter: drop-shadow(0 0 5px rgba(0, 243, 255, 0.5));
            transition: all 0.3s ease;
        }

        /* Image Preview Area */
        #previewContainer {
            display: none;
            margin-top: 1.5rem;
            position: relative;
            border-radius: 8px;
            border: 1px solid rgba(0, 243, 255, 0.3);
            overflow: hidden;
        }

        #imagePreview {
            width: 100%;
            display: block;
            filter: contrast(1.1) brightness(0.9);
        }

        /* Sci-Fi Laser Scanning Animation */
        .scanner {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--neon-cyan);
            box-shadow: 0 0 15px 5px var(--neon-cyan), 0 0 30px 15px rgba(0, 243, 255, 0.4);
            animation: scanLaser 2s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
            display: none;
        }

        @keyframes scanLaser {
            0% { top: 0%; }
            100% { top: 100%; }
        }

        /* Button Styling - Fixes Arial default */
        .btn {
            font-family: 'Orbitron', sans-serif;
            background: transparent;
            color: var(--neon-cyan);
            border: 1px solid var(--neon-cyan);
            width: 100%;
            padding: 1rem;
            border-radius: 4px;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            margin-top: 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.1) inset;
        }

        .btn:hover {
            background: var(--neon-cyan);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.6), 0 0 10px rgba(0, 243, 255, 0.4) inset;
        }

        .btn:disabled {
            border-color: #475569;
            color: #475569;
            background: transparent;
            box-shadow: none;
            cursor: not-allowed;
            text-shadow: none;
        }

        /* Modern Loading Text */
        #loadingText {
            display: none;
            text-align: center;
            margin-top: 1rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: 500;
            letter-spacing: 1px;
            color: var(--neon-pink);
            text-shadow: 0 0 8px rgba(255, 0, 234, 0.5);
            animation: glitch 1.5s infinite;
        }

        @keyframes glitch {
            0%, 100% { opacity: 1; transform: translateX(0); }
            33% { opacity: 0.8; transform: translateX(-1px); }
            66% { opacity: 0.9; transform: translateX(1px); }
        }

        /* Results Table - Dark Tech UI */
        #results {
            margin-top: 2rem;
            display: none;
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .results-header {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.25rem;
            color: var(--neon-cyan);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0, 243, 255, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 243, 255, 0.2);
        }

        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid rgba(0, 243, 255, 0.1);
        }

        th {
            background-color: rgba(0, 243, 255, 0.05);
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-cyan);
            font-weight: 500;
            font-size: 0.9rem;
            letter-spacing: 1px;
            width: 40%;
        }

        td {
            color: var(--text-main);
            font-weight: 400;
            font-family: 'Inter', monospace;
        }

        tr:hover td {
            background-color: rgba(0, 243, 255, 0.05);
        }

        .empty-field {
            color: #ef4444;
            font-style: italic;
            font-size: 0.9em;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <h2>PASSPORT_DATA_AI</h2>
            <p>Awaiting valid ID datastream for visual parsing...</p>
        </div>

        <form id="uploadForm">
            <div class="upload-area" id="dropzone">
                <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <div id="uploadText">
                    <strong>INITIALIZE UPLOAD</strong><br>
                    <span style="font-size: 0.85rem; color: #8b9bb4; margin-top: 6px; display: block; font-family: 'Inter', sans-serif;">PNG // JPG // JPEG</span>
                </div>
                <input type="file" id="imageInput" name="image" accept=".png, .jpg, .jpeg, .webp" required>
            </div>

            <div id="previewContainer">
                <img id="imagePreview" src="" alt="Passport Preview">
                <div class="scanner" id="scannerLine"></div>
            </div>

            <button type="submit" class="btn" id="submitBtn">Execute Scan</button>
            <div id="loadingText">DECRYPTING VISUAL DATA...</div>
        </form>

        <div id="results">
            <div class="results-header">Extracted Datapoints</div>
            <div id="resultContent"></div>
        </div>
    </div>

    <script>
        const imageInput = document.getElementById('imageInput');
        const previewContainer = document.getElementById('previewContainer');
        const imagePreview = document.getElementById('imagePreview');
        const uploadText = document.getElementById('uploadText');
        const submitBtn = document.getElementById('submitBtn');
        const loadingText = document.getElementById('loadingText');
        const scannerLine = document.getElementById('scannerLine');
        const resultsDiv = document.getElementById('results');

        // Handle Image Preview
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    previewContainer.style.display = 'block';
                    uploadText.innerHTML = `<strong style="color: var(--neon-cyan)">TARGET ACQUIRED:</strong> <br><span style="font-family:'Inter'; font-size:0.9rem;">${file.name}</span>`;
                    resultsDiv.style.display = 'none';
                }
                reader.readAsDataURL(file);
            } else {
                previewContainer.style.display = 'none';
                uploadText.innerHTML = `<strong>INITIALIZE UPLOAD</strong><br><span style="font-size: 0.85rem; color: #8b9bb4; margin-top: 6px; display: block; font-family: 'Inter', sans-serif;">PNG // JPG // JPEG</span>`;
            }
        });

        // Handle Form Submission
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = imageInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('image', file);

            // UI Loading State
            submitBtn.disabled = true;
            submitBtn.innerText = 'PROCESSING...';
            loadingText.style.display = 'block';
            scannerLine.style.display = 'block'; 
            resultsDiv.style.display = 'none';

            try {
                const response = await fetch('/web-extract', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('SYSTEM ERROR: ' + data.error);
                } else {
                    const contentDiv = document.getElementById('resultContent');
                    contentDiv.innerHTML = '';
                    
                    let extractedData;
                    try {
                        extractedData = typeof data.extracted_data === 'string' 
                            ? JSON.parse(data.extracted_data) 
                            : data.extracted_data;
                    } catch (parseErr) {
                        contentDiv.innerHTML = `<div style="color:#ff00ea; padding: 1rem; border: 1px solid #ff00ea;"><strong>PARSE ERROR. Raw output:</strong><br><code>${data.extracted_data}</code></div>`;
                        resultsDiv.style.display = 'block';
                        return;
                    }

                    // Build Cyberpunk Table
                    let tableHTML = '<table><tbody>';
                    for (const [key, value] of Object.entries(extractedData)) {
                        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        let displayValue = value ? value : `<span class="empty-field">NULL_VALUE</span>`;
                        
                        tableHTML += `<tr>
                            <th>${formattedKey}</th>
                            <td>${displayValue}</td>
                        </tr>`;
                    }
                    tableHTML += '</tbody></table>';
                    contentDiv.innerHTML = tableHTML;
                    
                    resultsDiv.style.display = 'block';
                    
                    setTimeout(() => {
                        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                }
            } catch (err) {
                console.error(err);
                alert('CRITICAL FAILURE DURING EXTRACTION.');
            } finally {
                // Reset UI Loading State
                submitBtn.disabled = false;
                submitBtn.innerText = 'EXECUTE SCAN';
                loadingText.style.display = 'none';
                scannerLine.style.display = 'none'; 
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
        "model": "google/gemini-3-flash-preview:online", 
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
            "allow_fallbacks": False,
            "sort": "throughput"
        }
    }

    # FIXED: Restored plain URL to prevent "No connection adapters" error
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
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {MY_APP_API_KEY}":
        return jsonify({"error": "Unauthorized. Invalid or missing API key."}), 401

    try:
        if 'image' in request.files:
            file = request.files['image']
            base64_image = base64.b64encode(file.read()).decode('utf-8')
            mime_type = file.mimetype or 'image/jpeg'
        elif request.is_json and 'image_base64' in request.json:
            base64_image = request.json['image_base64']
            mime_type = request.json.get('mime_type', 'image/jpeg')
        else:
            return jsonify({"error": "Must provide 'image' file or JSON with 'image_base64'"}), 400

        result_string = process_passport_image(base64_image, mime_type)
        return jsonify({
            "status": "success",
            "data": json.loads(result_string) 
        })

    except json.JSONDecodeError:
        return jsonify({"error": "LLM returned invalid JSON format", "raw_output": result_string}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")