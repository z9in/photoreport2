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
        site_name = request.form.get('site_name', '기본현장').strip()
        section_name = request.form.get('section_name', '기본구역').strip()
        
        # 현장명과 구역명으로 서버 내에 물리적인 폴더 생성
        # 예: static/shared_uploads/도서관공사/1.공사전사진/
        target_folder = os.path.join(BASE_UPLOAD_FOLDER, site_name, section_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        for file in files:
            if file.filename == '':
                continue
            if file:
                # 여러 사람이 올려도 덮어쓰기 되지 않도록 파일명 유지하여 저장
                filepath = os.path.join(target_folder, file.filename)
                file.save(filepath)
                
        return redirect(url_for('index'))

    # 현재 서버에 등록된 모든 현장(폴더) 목록 읽어오기
    sites = []
    if os.path.exists(BASE_UPLOAD_FOLDER):
        sites = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]

    return render_template('index.html', sites=sites, selected_site=None, section_photos=None)


@app.route('/view/<site_name>')
def view_site(site_name):
    """관리자가 특정 현장을 선택했을 때, 그 현장의 모든 구역과 사진을 일괄 로드"""
    site_path = os.path.join(BASE_UPLOAD_FOLDER, site_name)
    section_photos = {}

    if os.path.exists(site_path):
        # 현장 폴더 안의 모든 하위 구역 폴더들을 탐색
        sections = [d for d in os.listdir(site_path) if os.path.isdir(os.path.join(site_path, d))]
        
        for sec in sections:
            section_photos[sec] = []
            sec_path = os.path.join(site_path, sec)
            # 해당 구역 폴더 안의 이미지 파일들을 전부 긁어옴
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.GIF', '*.JPG', '*.JPEG', '*.PNG'):
                for file_p in glob.glob(os.path.join(sec_path, ext)):
                    filename = os.path.basename(file_p)
                    photo_name = os.path.splitext(filename)[0]
                    # 웹에서 접근 가능한 경로 생성 (/static/shared_uploads/...)
                    web_url = '/' + file_p.replace('\\', '/')
                    
                    section_photos[sec].append({
                        'url': web_url,
                        'name': photo_name
                    })

    # 다시 메인 화면을 보여주되, 선택된 현장의 데이터들을 채워서 보여줌
    sites = [d for d in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, d))]
    return render_template('index.html', sites=sites, selected_site=site_name, section_photos=section_photos)


@app.route('/clear/<site_name>', methods=['POST'])
def clear_site(site_name):
    """특정 현장의 사진 데이터를 서버에서 완전히 삭제 (초기화)"""
    import shutil
    site_path = os.path.join(BASE_UPLOAD_FOLDER, site_name)
    if os.path.exists(site_path):
        shutil.rmtree(site_path) # 폴더 통째로 삭제
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # host='0.0.0.0'으로 해야 같은 와이파이/네트워크의 다른 사람(폰)이 접속 가능합니다.