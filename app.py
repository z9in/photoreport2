import os
import glob
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_UPLOAD_FOLDER = os.path.join('static', 'shared_uploads')
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)

def make_safe_name(name):
    keepcharacters = (' ', '.', '_', '-')
    safe_name = "".join(c for c in name if c.isalnum() or c in keepcharacters).strip()
    return safe_name if safe_name else "unnamed"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photos' not in request.files:
            return redirect(request.url)
        
        files = request.files.getlist('photos')
        site_name = make_safe_name(request.form.get('site_name', '기본현장'))
        section_name = make_safe_name(request.form.get('section_name', '기본구역'))
        process_name = make_safe_name(request.form.get('process_name', '기본공정'))
        
        target_folder = os.path.join(BASE_UPLOAD_FOLDER, site_name, section_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        for index, file in enumerate(files):
            if file.filename == '':
                continue
            if file:
                ext = os.path.splitext(secure_filename(file.filename))[1].lower()
                if not ext:
                    ext = '.jpg'
                
                base_path = os.path.join(target_folder, f"{process_name}{ext}")
                
                if len(files) > 1 or os.path.exists(base_path):
                    counter = index + 1
                    while True:
                        new_filename = f"{process_name}_{counter}{ext}"
                        if not os.path.exists(os.path.join(target_folder, new_filename)):
                            break
                        counter += 1
                else:
                    new_filename = f"{process_name}{ext}"
                
                filepath = os.path.join(target_folder, new_filename)
                file.save(filepath)
                
        return redirect(url_for('index'))

    sites = []
    if os.path.exists(BASE_UPLOAD_FOLDER):
        sites = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]

    return render_template('index.html', sites=sites, selected_site=None, section_photos=None)

@app.route('/view/<path:site_name>')
def view_site(site_name):
    safe_site_name = make_safe_name(site_name)
    site_path = os.path.join(BASE_UPLOAD_FOLDER, safe_site_name)
    section_photos = {}

    if os.path.exists(site_path):
        sections = [d for d in os.listdir(site_path) if os.path.isdir(os.path.join(site_path, d))]
        
        for sec in sections:
            sec_path = os.path.join(site_path, sec)
            all_files = []
            
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.GIF', '*.JPG', '*.JPEG', '*.PNG'):
                all_files.extend(glob.glob(os.path.join(sec_path, ext)))
            
            # ★ 업로드된 물리적 시간(수정 시간) 기준으로 오름차순 정렬
            all_files.sort(key=os.path.getmtime)
            
            section_photos[sec] = []
            for file_p in all_files:
                filename = os.path.basename(file_p)
                photo_name = os.path.splitext(filename)[0]
                web_url = '/' + file_p.replace('\\', '/')
                
                section_photos[sec].append({
                    'url': web_url,
                    'name': photo_name
                })

    sites = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]
    return render_template('index.html', sites=sites, selected_site=safe_site_name, section_photos=section_photos)

@app.route('/clear/<path:site_name>', methods=['POST'])
def clear_site(site_name):
    import shutil
    safe_site_name = make_safe_name(site_name)
    site_path = os.path.join(BASE_UPLOAD_FOLDER, safe_site_name)
    if os.path.exists(site_path):
        shutil.rmtree(site_path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
