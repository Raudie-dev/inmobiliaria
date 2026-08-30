import os
import shutil

# Fix app1
app1_src = 'app1/templates/app1'
app1_dst = 'app1/templates'
if os.path.exists(app1_src):
    for f in os.listdir(app1_src):
        shutil.move(os.path.join(app1_src, f), os.path.join(app1_dst, f))
    os.rmdir(app1_src)

# Fix app2
app2_src = 'app2/templates/app2'
app2_dst = 'app2/templates'
if os.path.exists(app2_src):
    for f in os.listdir(app2_src):
        src_path = os.path.join(app2_src, f)
        dst_path = os.path.join(app2_dst, f)
        # Fix extends in file
        with open(src_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = content.replace("{% extends 'app2/base.html' %}", "{% extends 'base.html' %}")
        with open(dst_path, 'w', encoding='utf-8') as file:
            file.write(content)
        os.remove(src_path)
    os.rmdir(app2_src)

print("Templates moved and fixed.")
