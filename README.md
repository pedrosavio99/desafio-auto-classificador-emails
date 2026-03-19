# Classificador de Emails com IA – AutoU

Classificador automático de emails recebidos pela equipe da AutoU.  
Utiliza IA (Groq + Llama 3.3 70B) para categorizar emails como **Produtivo** ou **Improdutivo** e sugerir respostas automáticas profissionais.

**Objetivo do projeto**: Liberar tempo da equipe financeira eliminando a leitura manual de emails irrelevantes ou repetitivos.

## Tecnologias Utilizadas

- Backend: Python + Flask
- IA / LLM: Groq Cloud (modelo: llama-3.3-70b-versatile)
- Processamento de PDF: pdfplumber
- Frontend: HTML + Bootstrap 5 (via CDN)
- Outras: python-dotenv, werkzeug

## Funcionalidades

- Upload de arquivos .txt ou .pdf
- Inserção direta de texto do email
- Classificação automática: Produtivo / Improdutivo
- Sugestão de resposta automática assinada pela "Equipe AutoU"
- Interface responsiva e intuitiva
- Exemplos demonstrativos na página inicial

## Como Rodar Localmente

1. Clone o repositório:
   git https://github.com/pedrosavio99/desafio-auto-classificador-emails

   cd desafio-auto-classificador-emails

2. Crie e ative o ambiente virtual:
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate

3. Instale as dependências:
   pip install -r requirements.txt

4. Crie o arquivo .env na raiz com sua chave Groq:
   GROQ_API_KEY=gsk_sua_chave_aqui

5. Execute a aplicação:
   python app.py

6. Abra no navegador: http://127.0.0.1:5000/



## Exemplo de Uso

**Email Produtivo (cole no campo):**

Olá equipe AutoU,

Gostaria de saber o status da minha solicitação de limite de crédito. Protocolo 456789.
Enviei os documentos na semana passada.

Obrigado,
Ana Costa

**Resposta esperada (gerada pela IA):**

Categoria: Produtivo

Justificativa: Solicitação de atualização de status de protocolo em andamento.

Resposta sugerida: Prezada Ana, confirmamos o recebimento da sua solicitação (protocolo 456789). Estamos analisando o status e retornaremos em breve com as informações atualizadas. Atenciosamente, Equipe AutoU



## Autor

Pedro Savio  
GitHub: https://github.com/pedrosavio99  
Local: Campina Grande, PB

Projeto desenvolvido para o desafio da AutoU – Março 2026