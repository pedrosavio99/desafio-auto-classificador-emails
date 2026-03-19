from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_key_muito_segura_aqui'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limite

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuração da Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt atualizado com contexto da AutoU
SYSTEM_PROMPT = """
Você é um assistente de email inteligente da **AutoU**, uma grande empresa do setor financeiro.
Sua tarefa é classificar emails recebidos pela equipe da AutoU e sugerir respostas automáticas adequadas.

1. CLASSIFIQUE o email em APENAS UMA das duas categorias:
   - Produtivo: emails que exigem ação, resposta, acompanhamento ou análise pela equipe (ex.: solicitação de status, dúvida sobre produto/serviço, envio de documento importante, reclamação, suporte técnico, atualização de caso).
   - Improdutivo: emails que não demandam ação imediata (ex.: felicitações, feliz natal/ano novo, bom dia/tarde, agradecimento genérico, spam leve, forward irrelevante, piadas).

2. SUGIRA UMA RESPOSTA AUTOMÁTICA curta, profissional e educada, assinada sempre como "Equipe AutoU".

REGRAS OBRIGATÓRIAS:
- Responda SOMENTE com JSON válido, sem qualquer texto antes ou depois.
- Estrutura EXATA do JSON:
{
  "categoria": "Produtivo" ou "Improdutivo",
  "justificativa": "explicação curta e objetiva de no máximo 1 frase sobre o motivo da classificação",
  "resposta_sugerida": "texto completo da resposta automática (máximo 5-6 linhas, linguagem formal em português brasileiro, assinatura final obrigatória: 'Atenciosamente, Equipe AutoU')"
}
- Sempre use português brasileiro formal e corporativo.
- A resposta sugerida deve ser pronta para envio, incluindo saudação e despedida quando apropriado.
- Se o email for muito curto ou ambíguo, classifique com base no conteúdo principal e justifique.
"""

def classificar_email_com_groq(texto_email):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Email recebido:\n\n{texto_email}"}
            ],
            temperature=0.2,
            max_tokens=700,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na chamada Groq: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    texto_email = ""

    # Prioridade: texto colado
    if request.form.get('texto_email', '').strip():
        texto_email = request.form['texto_email'].strip()

    # Se não, tenta arquivo
    elif 'arquivo' in request.files:
        file = request.files['arquivo']
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'warning')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            try:
                if file.filename.lower().endswith('.txt'):
                    texto_email = file.read().decode('utf-8', errors='ignore').strip()
                elif file.filename.lower().endswith('.pdf'):
                    with pdfplumber.open(file) as pdf:
                        texto_email = "\n\n".join(
                            page.extract_text() or "" for page in pdf.pages
                        ).strip()
            except Exception as e:
                flash(f'Erro ao ler o arquivo: {str(e)}', 'danger')
                return redirect(url_for('index'))
        else:
            flash('Formato inválido. Apenas .txt ou .pdf são permitidos.', 'danger')
            return redirect(url_for('index'))

    if not texto_email:
        flash('Nenhum conteúdo de email foi enviado ou extraído.', 'warning')
        return redirect(url_for('index'))

    # Chama a Groq
    resultado_json = classificar_email_com_groq(texto_email)

    if not resultado_json:
        flash('Não foi possível conectar com a IA. Verifique sua chave Groq ou tente novamente.', 'danger')
        return redirect(url_for('index'))

    try:
        resultado = json.loads(resultado_json)
    except:
        flash('Resposta da IA veio em formato inválido.', 'danger')
        return redirect(url_for('index'))

    return render_template(
        'resultado.html',
        texto_extraido=texto_email,
        categoria=resultado.get('categoria', 'Erro'),
        justificativa=resultado.get('justificativa', 'Não gerada'),
        resposta_sugerida=resultado.get('resposta_sugerida', 'Não gerada')
    )

if __name__ == '__main__':
    app.run(debug=True)