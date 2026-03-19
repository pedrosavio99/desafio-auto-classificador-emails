from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import pdfplumber
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

app = Flask(__name__)
app.secret_key = 'super_secret_key_muito_segura'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuração Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt poderoso (bem estruturado e restritivo)
SYSTEM_PROMPT = """
Você é um classificador inteligente de emails corporativos para uma grande empresa financeira.
Sua tarefa é:

1. CLASSIFICAR o email em APENAS uma das duas categorias:
   - Produtivo: requer ação, resposta ou acompanhamento (ex: solicitação de status, dúvida sobre sistema, envio de arquivo importante, reclamação, pedido de suporte).
   - Improdutivo: não requer ação imediata (ex: feliz natal, bom dia, agradecimento genérico, spam leve, piada, forward irrelevante).

2. SUGERIR UMA RESPOSTA AUTOMÁTICA curta, profissional e adequada à categoria:
   - Para Produtivo: educada, confirmando recebimento + informando próximo passo ou pedindo mais detalhes se necessário.
   - Para Improdutivo: educada, breve, agradecendo ou encerrando sem abrir precedentes.

REGRAS OBRIGATÓRIAS:
- Responda APENAS com JSON válido, sem texto extra antes ou depois.
- Estrutura EXATA:
{
  "categoria": "Produtivo" ou "Improdutivo",
  "justificativa": "explicação curta de 1 frase do porquê da categoria",
  "resposta_sugerida": "texto da resposta automática (máx 4-6 linhas)"
}
- Sempre use português brasileiro formal e profissional.
- Seja objetivo e direto.
"""

def classificar_email_com_groq(texto_email):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ou "mixtral-8x7b-32768" se preferir mais rápido
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Email recebido:\n\n{texto_email}\n\nClassifique e sugira resposta."}
            ],
            temperature=0.2,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    texto_email = ""

    # 1. Texto colado
    if 'texto_email' in request.form and request.form['texto_email'].strip():
        texto_email = request.form['texto_email'].strip()

    # 2. Arquivo upload
    elif 'arquivo' in request.files:
        file = request.files['arquivo']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            if file.filename.endswith('.txt'):
                texto_email = file.read().decode('utf-8', errors='ignore').strip()
            elif file.filename.endswith('.pdf'):
                try:
                    with pdfplumber.open(file) as pdf:
                        texto_email = "\n\n".join(page.extract_text() or "" for page in pdf.pages).strip()
                except Exception as e:
                    flash(f'Erro ao ler PDF: {str(e)}', 'danger')
                    return redirect(url_for('index'))
        else:
            flash('Formato inválido. Use .txt ou .pdf', 'danger')
            return redirect(url_for('index'))

    else:
        flash('Envie texto ou arquivo', 'danger')
        return redirect(url_for('index'))

    if not texto_email:
        flash('Não foi possível extrair texto', 'warning')
        return redirect(url_for('index'))

    # Chama Groq
    resultado_json = classificar_email_com_groq(texto_email)

    if resultado_json is None:
        flash('Erro ao conectar com a IA. Verifique sua chave Groq.', 'danger')
        return redirect(url_for('index'))

    import json
    try:
        resultado = json.loads(resultado_json)
    except:
        flash('Resposta da IA inválida', 'danger')
        return redirect(url_for('index'))

    return render_template('resultado.html',
                           texto_extraido=texto_email,
                           categoria=resultado.get('categoria', 'Erro'),
                           justificativa=resultado.get('justificativa', ''),
                           resposta_sugerida=resultado.get('resposta_sugerida', 'Sem sugestão disponível'))

if __name__ == '__main__':
    app.run(debug=True)