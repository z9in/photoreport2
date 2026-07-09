import os
import glob
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 사진이 영구 저장될 루트 폴더
BASE_UPLOAD_FOLDER = os.path.join('static', 'shared_uploads')
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photos' not in request.files:
            return redirect(request.url)
        
        files = request.files.getlist('photos')
        process_name = request.form.get('process_name', '기본 공정').strip()
        section_name = request.form.get('section_name', '기본 구역').strip()
        
        # 장소 및 공정명 -> 구역명 구조로 서버 내에 물리 폴더 생성
        target_folder = os.path.join(BASE_UPLOAD_FOLDER, process_name, section_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        for file in files:
            if file.filename == '':
                continue
            if file:
                filepath = os.path.join(target_folder, file.filename)
                file.save(filepath)
                
        return redirect(url_for('index'))

    # 현재 서버에 등록된 모든 '장소 및 공정' 목록 읽어오기
    processes = []
    if os.path.exists(BASE_UPLOAD_FOLDER):
        processes = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]

    return render_template('index.html', processes=processes, selected_process=None, section_photos=None)


@app.route('/view/<path:process_name>')
def view_process(process_name):
    """선택한 장소 및 공정의 모든 구역과 사진을 일괄 로드"""
    process_path = os.path.join(BASE_UPLOAD_FOLDER, process_name)
    section_photos = {}

    if os.path.exists(process_path):
        sections = [d for d in os.listdir(process_path) if os.path.isdir(os.path.join(process_path, d))]
        
        for sec in sections:
            section_photos[sec] = []
            sec_path = os.path.join(process_path, sec)
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.GIF', '*.JPG', '*.JPEG', '*.PNG'):
                for file_p in glob.glob(os.path.join(sec_path, ext)):
                    filename = os.path.basename(file_p)
                    photo_name = os.path.splitext(filename)[0]
                    web_url = '/' + file_p.replace('\\', '/')
                    
                    section_photos[sec].append({
                        'url': web_url,
                        'name': photo_name
                    })

    processes = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]
    return render_template('index.html', processes=processes, selected_process=process_name, section_photos=section_photos)


@app.route('/clear/<path:process_name>', methods=['POST'])
def clear_process(process_name):
    """해당 데이터 서버에서 영구 삭제"""
    import shutil
    process_path = os.path.join(BASE_UPLOAD_FOLDER, process_name)
    if os.path.exists(process_path):
        shutil.rmtree(process_path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)