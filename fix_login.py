import os

files = ['app.py', 'sales.py', 'inventory.py']
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('url_for("login")', 'url_for("web_login")')
    content = content.replace("url_for('login')", "url_for('web_login')")
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
