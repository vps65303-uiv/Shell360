from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <div style='text-align:center; margin-top:50px; font-family:sans-serif;'>
        <h1 style='color:#0f0;'>🚀 تم الاتصال بنجاح يا محمد!</h1>
        <p>السيرفر متصل الآن بـ Ngrok الخاص بهاتفك.</p>
    </div>
    """

if __name__ == '__main__':
    # يستمع السيرفر على البورت 8443
    app.run(host='0.0.0.0', port=8443)
    
