import torch
from PIL import Image
import os
import uuid
from flask import Flask, request, render_template, send_file
from RealESRGAN import RealESRGAN

app = Flask(__name__)
app.static_folder = 'uploads'  # Serve the 'uploads' directory

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load 2x and 4x models
model_2x_path = 'models/RealESRGAN_x2.pth'  # Path relative to the application directory
model_4x_path = 'models/RealESRGAN_x4.pth'  # Path relative to the application directory

model_2x = RealESRGAN(device, scale=2)
model_2x.load_weights(model_2x_path)

model_4x = RealESRGAN(device, scale=4)
model_4x.load_weights(model_4x_path)

# Function to handle image upscaling based on the selected model
def upscale_image(image_file, scale_factor):
    image = Image.open(image_file).convert('RGB')
    if scale_factor == '2':
        model = model_2x
    elif scale_factor == '4':
        model = model_4x
    else:
        return None, None
    
    sr_image = model.predict(image)
    filename = f'upscaled_{uuid.uuid4()}.png'
    save_dir = 'uploads'
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    sr_image.save(file_path)
    return file_path, filename

@app.route('/', methods=['GET', 'POST'])
def upload_and_display():
    if request.method == 'POST' and 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename == '':
            return render_template('Image Upscale & Enhance.html', message='Please select an image')
        try:
            scale_factor = request.form.get('scale_factor')
            file_path, filename = upscale_image(image_file, scale_factor)
            if file_path:
                upscaled_image_url = f'{filename}'
                return render_template('Image Upscale & Enhance.html', message='Image upscaled successfully!', upscaled_image=upscaled_image_url)
            else:
                return render_template('Image Upscale & Enhance.html', message='Invalid scale factor selected.')
        except Exception as e:
            print(f'Error: {e}')
            return render_template('Image Upscale & Enhance.html', message='An error occurred during processing.')
    else:
        return render_template('Image Upscale & Enhance.html')

@app.route('/download/<filename>')
def download_image(filename):
    try:
        file_path = os.path.join('uploads', filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return "File not found"

if __name__ == '__main__':
    app.run(debug=True)
