from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import pdfplumber

app = Flask(__name__)
app.secret_key = 'super_secret_key_muito_segura'  # Necessário para flash messages
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB no upload

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    texto_email = ""

    # 1. Verifica se veio texto colado
    if 'texto_email' in request.form and request.form['texto_email'].strip():
        texto_email = request.form['texto_email'].strip()

    # 2. Verifica se veio arquivo
    elif 'arquivo' in request.files:
        file = request.files['arquivo']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Lê o conteúdo sem salvar no disco (melhor para deploy)
            if filename.endswith('.txt'):
                texto_email = file.read().decode('utf-8', errors='ignore').strip()
            elif filename.endswith('.pdf'):
                try:
                    with pdfplumber.open(file) as pdf:
                        texto_email = ""
                        for page in pdf.pages:
                            texto_email += page.extract_text() or "" + "\n\n"
                    texto_email = texto_email.strip()
                except Exception as e:
                    flash(f'Erro ao ler PDF: {str(e)}', 'danger')
                    return redirect(url_for('index'))
        else:
            flash('Formato de arquivo não permitido. Use .txt ou .pdf', 'danger')
            return redirect(url_for('index'))

    else:
        flash('Nenhum texto ou arquivo foi enviado', 'danger')
        return redirect(url_for('index'))

    if not texto_email:
        flash('Não foi possível extrair texto do email', 'warning')
        return redirect(url_for('index'))

    # Por enquanto só mostramos o texto extraído (depois vamos enviar pro Groq)
    return render_template('resultado.html', texto_extraido=texto_email)

if __name__ == '__main__':
    app.run(debug=True)