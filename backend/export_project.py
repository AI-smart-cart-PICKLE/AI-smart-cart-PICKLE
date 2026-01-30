import os
import sys

# 1. 내용을 추출하고 싶은 파일 확장자들
TARGET_EXTENSIONS = {'.py', '.sql', '.md', '.txt', '.env'} 

# 2. 무시할 폴더 및 파일
IGNORE_DIRS = {'.git', '__pycache__', 'venv', '.venv', '.idea', '.vscode', 'migrations'}
IGNORE_FILES = {'export_project.py', 'poetry.lock', 'package-lock.json', 'project_context.txt'}

# 윈도우 인코딩 문제 방지를 위해 출력 강제 설정
sys.stdout.reconfigure(encoding='utf-8')

def print_tree(startpath):
    print(f"\n[Project Structure]: {startpath}")
    print("=" * 40)
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in IGNORE_FILES:
                print(f'{subindent}{f}')
    print("=" * 40 + "\n")

def export_files(startpath):
    print("[File Contents]")
    print("=" * 40)
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file in IGNORE_FILES:
                continue
            
            _, ext = os.path.splitext(file)
            if ext not in TARGET_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, startpath)

            print(f"\nStart of file: {relative_path}")
            print("-" * 40)
            try:
                # 파일을 읽을 때 에러가 나면 건너뜀
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    print(f.read())
            except Exception as e:
                print(f"Error reading file: {e}")
            print("-" * 40)
            print(f"End of file: {relative_path}\n")

if __name__ == "__main__":
    current_dir = os.getcwd()
    # 필요하면 특정 폴더(app)만 지정 가능:
    # current_dir = os.path.join(os.getcwd(), 'app')
    
    print_tree(current_dir)
    export_files(current_dir)