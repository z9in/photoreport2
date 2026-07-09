import os
import glob
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_UPLOAD_FOLDER = os.path.join('static', 'shared_uploads')
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photos' not in request.files:
            return redirect(request.url)
        
        files = request.files.getlist('photos')
        site_name = request.form.get('site_name', '기본현장').strip()
        section_name = request.form.get('section_name', '기본구역').strip()
        process_name = request.form.get('process_name', '기본공정').strip()
        
        # 물리적인 폴더 구조는 [현장 명] -> [구역 명] 구조로 생성합니다.
        target_folder = os.path.join(BASE_UPLOAD_FOLDER, site_name, section_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # 사용자가 지정한 '장소 및 공정 명'을 기반으로 파일명을 강제 지정하여 저장합니다.
        for index, file in enumerate(files):
            if file.filename == '':
                continue
            if file:
                ext = os.path.splitext(file.filename)[1].lower() # 확장자 추출 (.jpg, .png 등)
                
                # 동일한 공정명으로 여러 장이 올라왔을 때 덮어쓰기 방지를 위한 넘버링 처리
                # 예: 도서관복도_1.jpg, 도서관복도_2.jpg
                if len(files) > 1:
                    new_filename = f"{process_name}_{index + 1}{ext}"
                else:
                    # 한 장만 올렸을 때도 기존 파일이 있으면 번호 부여
                    base_path = os.path.join(target_folder, f"{process_name}{ext}")
                    if os.path.exists(base_path):
                        new_filename = f"{process_name}_{index + 1}{ext}"
                    else:
                        new_filename = f"{process_name}{ext}"
                
                filepath = os.path.join(target_folder, new_filename)
                file.save(filepath)
                
        return redirect(url_for('index'))

    # 현재 서버에 등록된 모든 [현장 명] 목록 읽어오기
    sites = []
    if os.path.exists(BASE_UPLOAD_FOLDER):
        sites = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]

    return render_template('index.html', sites=sites, selected_site=None, section_photos=None)


@app.route('/view/<path:site_name>')
def view_site(site_name):
    """선택한 현장 명의 모든 구역과 사진을 일괄 로드"""
    site_path = os.path.join(BASE_UPLOAD_FOLDER, site_name)
    section_photos = {}

    if os.path.exists(site_path):
        sections = [d for d in os.listdir(site_path) if os.path.isdir(os.path.join(site_path, d))]
        
        for sec in sections:
            section_photos[sec] = []
            sec_path = os.path.join(site_path, sec)
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.GIF', '*.JPG', '*.JPEG', '*.PNG'):
                for file_p in glob.glob(os.path.join(sec_path, ext)):
                    filename = os.path.basename(file_p)
                    photo_name = os.path.splitext(filename)[0]
                    web_url = '/' + file_p.replace('\\', '/')
                    
                    section_photos[sec].append({
                        'url': web_url,
                        'name': photo_name
                    })

    sites = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]
    return render_template('index.html', sites=sites, selected_site=site_name, section_photos=section_photos)


@app.route('/clear/<path:site_name>', methods=['POST'])
def clear_site(site_name):
    """해당 현장 데이터 서버에서 영구 삭제"""
    import shutil
    site_path = os.path.join(BASE_UPLOAD_FOLDER, site_name)
    if os.path.exists(site_path):
        shutil.rmtree(site_path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)