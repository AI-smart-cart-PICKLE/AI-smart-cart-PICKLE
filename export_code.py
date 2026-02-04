import os

# ---------------------------------------------------------
# 설정: 코드를 추출할 대상 폴더와 제외할 폴더
# ---------------------------------------------------------
TARGET_EXTENSIONS = {'.dart', '.py', '.yaml', '.yml', '.env', '.sql', '.md'} # 가져올 파일 확장자
IGNORE_DIRS = {
    '.git', '.idea', '.vscode', '.dart_tool', 'build', '.pub-cache', # 설정/빌드 폴더 제외
    'android', 'ios', 'web', 'linux', 'macos', 'windows', # 플랫폼 폴더 제외 (용량 큼)
    'venv', '__pycache__', 'node_modules', 'migrations', # 백엔드 잡동사니 제외
    'assets', 'images' # 이미지 제외
}
OUTPUT_FILE = "project_code_summary.txt"

def is_ignored(path):
    # 경로 중에 제외할 폴더가 포함되어 있는지 확인
    parts = path.split(os.sep)
    for part in parts:
        if part in IGNORE_DIRS:
            return True
    return False

def collect_code():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # 현재 폴더부터 하위 폴더 탐색
        for root, dirs, files in os.walk("."):
            # 제외할 폴더는 탐색하지 않음
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 제외할 폴더 안에 있는 파일이거나, 확장자가 안 맞으면 패스
                if is_ignored(file_path): 
                    continue
                
                _, ext = os.path.splitext(file)
                if ext.lower() not in TARGET_EXTENSIONS:
                    continue
                
                # 내 자신(스크립트)은 제외
                if file == "export_code.py" or file == OUTPUT_FILE:
                    continue

                # 파일 내용을 읽어서 출력 파일에 쓰기
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        
                        outfile.write(f"\n{'='*50}\n")
                        outfile.write(f"FILE PATH: {file_path}\n")
                        outfile.write(f"{'='*50}\n")
                        outfile.write(content + "\n")
                        print(f"✅ 추가됨: {file_path}")
                except Exception as e:
                    print(f"❌ 읽기 실패 (스킵): {file_path} / {e}")

    print(f"\n🎉 완료! '{OUTPUT_FILE}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    collect_code()