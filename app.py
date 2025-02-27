import streamlit as st
from utils import chatbot, text
from streamlit_chat import message

def main():
    st.set_page_config(page_title='TalktoPDF - PS', page_icon=':books:')
    col1, col2 = st.columns(2)

    with col1:
        modelos_disponiveis = ['Llama 3.3 70B', 'Llama 3.1 70B','Cohere Command-R','Cohere Command-R Plus']
        modelo_escolhido = st.selectbox("Escolha o modelo LLM", modelos_disponiveis)

    st.header('Converse com seus arquivos :paperclip:', divider="gray")

    # Inicializa o histórico de conversa como uma lista vazia, se ainda não existir
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None

    # Exibe a conversa anterior
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Captura a entrada do usuário
    if user_question := st.chat_input("Faça uma pergunta para mim!"):
        st.session_state.messages.append({"role": "user", "content": user_question})
        
        with st.chat_message("user"):
            st.markdown(user_question)

        # Gera a resposta do assistente
        if st.session_state.vectorstore is not None:
            vectorstore = st.session_state.vectorstore
            response = chatbot.create_conversation_chain(user_question, vectorstore, modelo_escolhido)

            # Adiciona a resposta do assistente ao histórico
            st.session_state.messages.append({"role": "assistant", "content": response})

            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            st.warning("Por favor, processe os arquivos PDF antes de fazer uma pergunta.")

    #for i, text_message in enumerate(st.session_state.conversation):
    #    if text_message["role"] == "user":
    #        message(text_message["content"], is_user=True, key=str(i) + '_user')
    #    else:
    #        message(text_message["content"], is_user=False, key=str(i) + '_bot')

    # Sidebar para upload de arquivos
    with st.sidebar:
        st.subheader('Seus arquivos')
        pdf_docs = st.file_uploader("Carregue os seus arquivos em formato pdf", accept_multiple_files=True)

        # Verifica se o botão "Processar" foi clicado
        processar_clicked = st.button('Processar')

        if processar_clicked:
            if pdf_docs:
                # Verifica se todos os arquivos são PDFs
                non_pdf_files = [file for file in pdf_docs if not file.name.endswith('.pdf')]

                if non_pdf_files:
                    st.warning(f"Alguns arquivos não são PDFs: {', '.join([file.name for file in non_pdf_files])}. Por favor, envie apenas PDFs.")
                else:
                    config = text.load_oci_config()
                    all_files_text = text.read_pdf(pdf_docs)
                    pdf_chunk = [chunk for chunk in text.text_chunk(all_files_text) if chunk.strip()]

                    # Cria o vectorstore e armazena na sessão
                    vectorstore = chatbot.create_vectorstore(pdf_chunk, config)
                    st.session_state.vectorstore = vectorstore
                    st.success('Arquivos processados com sucesso! Agora você pode fazer perguntas.')
            else:
                st.warning("Nenhum arquivo foi enviado. Por favor, envie ao menos um arquivo PDF.")

if __name__ == '__main__':
    main()