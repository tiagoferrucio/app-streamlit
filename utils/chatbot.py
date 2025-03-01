import os
import oci
import ads
from utils import text
import app

from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

def load_llm(config,model_id):
    chat_model = ChatOCIGenAI(
        model_id= model_id, ## meta.llama-3.3-70b-instruct, cohere.command-r-plus, cohere.command-r-16k
        service_endpoint="https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
        compartment_id='ocid1.compartment.oc1..aaaaaaaa7ni42qbrptng34mhf7i3e23lmxes734ovsggllryxrofxkgk6gda',
        model_kwargs={"temperature": 0.7, "max_tokens": 2000},
    )
    
    return chat_model

def load_embed(config):
    embed_model = OCIGenAIEmbeddings(
        model_id="cohere.embed-multilingual-v3.0", ## - cohere.command-r-plus, cohere.command-r-16k
        service_endpoint="https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
        compartment_id="ocid1.compartment.oc1..aaaaaaaa7ni42qbrptng34mhf7i3e23lmxes734ovsggllryxrofxkgk6gda",
    )
    
    return embed_model

def create_vectorstore(chunks,config):
    embeddings = load_embed(config)
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)

    return vectorstore

def create_conversation_chain(user_question, vectorstore, modelo_escolhido):
    config = text.load_oci_config()

    ##retriever = vectorstore.as_retriever()
    #result = vectorstore.similarity_search_with_score(user_question, k=30)
    #context = ' '.join([res[0].page_content for res in result])

    template = """
    Você é um chatbot projetado para auxiliar os usuários a tirar dúvidas sobre documentos.
    Responda em português;
    Use palavras que sua audiência vai entender;
    Siga um estilo para o seu texto; Evite palavras desnecessárias; Não seja redundante;
    Prefira discurso direto; Organize a informação por ordem de importância e uso;
    Use marcadores para organizar melhor as respostas ou listas quando necessário;
    Se o texto não contiver a resposta, responder que a resposta não está disponível.
    Mantenha as respostas precisas para a pergunta
    Responda apenas às perguntas com base no contexto fornecido abaixo:

    contexto: {context}
    
    Pergunta: {question};
    """
    prompt = PromptTemplate(
        input_variables=["context", "user_question"],
        template=template
    )
    chain_type_kwargs = {"prompt" : prompt}

    #['Llama 3.3 70B', 'Llama 3.1 70B','Llama 3.1 405B','Cohere Command-R', 'Cohere Command-R Plus']
    if modelo_escolhido == "Llama 3.3 70B":
        model_id = "meta.llama-3.3-70b-instruct"
    elif modelo_escolhido == "Llama 3.1 70B":
        model_id = "meta.llama-3.1-70b-instruct"
    elif modelo_escolhido == "Cohere Command-R":
        model_id = "cohere.command-r-08-2024"
    elif modelo_escolhido == "Cohere Command-R Plus":
        model_id = "cohere.command-r-plus-08-2024"

    llm = load_llm(config, model_id)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever= vectorstore.as_retriever(),
        memory = memory,
        combine_docs_chain_kwargs=chain_type_kwargs
    )   

    response  = conversation_chain.invoke({"question": user_question})
    #response = (prompt | llm).invoke({"context": context, "user_question": user_question})

    return(response.get("answer"))