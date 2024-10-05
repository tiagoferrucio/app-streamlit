import os
import oci
import ads
from utils import text

from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

def load_llm(config):
    chat_model = ChatOCIGenAI(
        model_id="cohere.command-r-16k", ## - cohere.command-r-plus, cohere.command-r-16k
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

def create_conversation_chain(user_question, vectorstore):
    config = text.load_oci_config()

    llm = load_llm(config)

    ##retriever = vectorstore.as_retriever()
    result = vectorstore.similarity_search_with_score(user_question, k=30)
    context = ' '.join([res[0].page_content for res in result])

    template = '''
    Você é um acessor juridico e precisa ajudar o time de vendas exclarecendo algumas dúvidas;

    Responda em português;
    Use palavras que sua audiência vai entender;
    Siga um estilo para o seu texto; Evite palavras desnecessárias; Não seja redundante;
    Prefira discurso direto; Organize a informação por ordem de importância e uso;
    Caso não saiba, não invente, diga que não sabe
    Responda somente baseado no contexto abaixo;

    contexto: {context}
    
    Pergunta: {user_question};
    '''
    prompt = PromptTemplate(
        input_variables=["context", "user_question"],
        template=template
    )

    response = (prompt | llm).invoke({"context": context, "user_question": user_question})

    return response.content