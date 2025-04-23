from flask import Flask, render_template, request, send_file, url_for
import os
from PIL import Image
import qrcode
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Dictionary to hold sessions
sessions = {}

@app.route('/')
def index():
    session_id = str(uuid.uuid4())[:8]  # Short random ID
    sessions[session_id] = []  # Initialize session
    
    # Generate QR code URL (FIXED: Use url_for for correct URL)
    session_url = url_for('upload', session_id=session_id, _external=True)
    
    # Save QR code
    qr_img = qrcode.make(session_url)
    qr_path = os.path.join('static', 'qr.png')
    qr_img.save(qr_path)
    
    return render_template('index.html', qr_url=qr_path, session_url=session_url)

@app.route('/session/<session_id>', methods=['GET', 'POST'])
def upload(session_id):
    if session_id not in sessions:
        return "Invalid session ID", 404  # Better error message

    if request.method == 'POST':
        uploaded_files = request.files.getlist('images')
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            return "No files uploaded!", 400

        images = []
        for file in uploaded_files:
            if file.filename == '':
                continue  # Skip empty files
            
            try:
                # Save the image temporarily
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(temp_path)
                
                # Convert to RGB (required for PDF)
                img = Image.open(temp_path).convert('RGB')
                images.append(img)
                
                # Delete the temp file
                os.remove(temp_path)
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")
                continue

        if not images:
            return "No valid images found!", 400

        # Generate PDF
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}.pdf')
        try:
            images[0].save(
                pdf_path,
                save_all=True,
                append_images=images[1:],
                quality=100
            )
            return send_file(pdf_path, as_attachment=True)
        except Exception as e:
            return f"Failed to generate PDF: {str(e)}", 500

    # GET request: Show upload page
    return render_template('upload.html', session_id=session_id)

if __name__ == '__main__':
    app.run(debug=True)