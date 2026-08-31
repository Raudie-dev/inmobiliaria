import os

directory = r'c:\Users\Rauly\Documents\Contenido de RauDie\Proyectos\inmobiliaria'
extensions = ['.html', '.css', '.py']

# First, rename the css file
old_css = os.path.join(directory, 'assets', 'css', 'inmobiliaria.css')
new_css = os.path.join(directory, 'assets', 'css', 'inmobiliaria.css')
if os.path.exists(old_css):
    os.rename(old_css, new_css)
    print(f'Renamed {old_css} to {new_css}')

for root, _, files in os.walk(directory):
    if '.git' in root or '.venv' in root or 'env' in root:
        continue
    for file in files:
        if any(file.endswith(ext) for ext in extensions):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace case-sensitive
                new_content = content.replace('Inmobiliaria', 'Inmobiliaria')
                new_content = new_content.replace('inmobiliaria', 'inmobiliaria')
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f'Updated {path}')
            except Exception as e:
                print(f'Error reading {path}: {e}')
