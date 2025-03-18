import streamlit as st
import requests
import json
import PyPDF2

# Função para extrair texto de um PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Função para interagir com o modelo de IA
def chat_with_llm(user_input, document_text):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + st.secrets["qwen_key"],
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "qwen/qwen2.5-vl-72b-instruct:free",
            "messages": [
                {"role": "system", "content": "Você é um assistente que responde com base no documento fornecido."},
                {"role": "user", "content": f"{document_text}\n\n{user_input}"},
            ],
        })
    )
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro ao obter resposta.")
    else:
        return "Erro ao acessar o modelo de IA."

# Interface Streamlit
st.title("Chatbot de Documentos (PDF/TXT)")

uploaded_file = st.file_uploader("Carregue um arquivo PDF ou TXT", type=["pdf", "txt"])

document_text = ""
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        document_text = extract_text_from_pdf(uploaded_file)
    else:
        document_text = uploaded_file.getvalue().decode("utf-8")
    
    st.text_area("Conteúdo do Documento", document_text[:1000] + "...", height=150)
    
    example_questions = [
        "Qual é o resumo do documento?",
        "Quais são os principais tópicos abordados?",
        "Pode listar os pontos mais importantes do documento?",
        "Qual é a conclusão do documento?",
        "O documento faz alguma recomendação?"
    ]
    
    st.write("### Perguntas sugeridas:")
    for q in example_questions:
        if st.button(q):
            response = chat_with_llm(q, document_text)
            st.write("#### Resposta:")
            st.write(response)
    
    user_input = st.text_input("Digite sua pergunta:")
    if user_input:
        response = chat_with_llm(user_input, document_text)
        st.write("#### Resposta:")
        st.write(response)
