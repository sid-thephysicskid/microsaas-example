import os
from typing import List

import streamlit as st
from st_paywall import add_auth
from st_paywall.aggregate_auth import handle_subscription_cancellation
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import TokenTextSplitter
from langchain_community.vectorstores import Chroma
from PyPDF2 import PdfReader

add_auth(
    required=True,
    login_button_text="Login with Google",
    login_button_color="#FD504D",
    login_sidebar=True,
    )

if "user_subscribed" in st.session_state and st.session_state.user_subscribed:
    if st.button("Cancel Subscription"):
        handle_subscription_cancellation()

def load_data(uploaded_file) -> str:
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[Document]:
    text_splitter = TokenTextSplitter(model_name="gpt-3.5-turbo-16k", chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    text_chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in text_chunks]
    return documents


def initialize_llm(model: str, temperature: float) -> ChatOpenAI:
    os.environ["OPENAI_API_KEY"]=st.secrets["OPENAI_API_KEY"]
    llm = ChatOpenAI(model=model, temperature=temperature)
    return llm


def generate_questions(llm: ChatOpenAI, chain_type: str, documents: List[Document]) -> str:
    prompt_template_questions = """
    You are an expert in creating practice questions based on study material.
    Your goal is to prepare a student for their an exam. You do this by asking questions about the text below:

    ------------
    {text}
    ------------

    Create questions that will prepare the student for their exam. Make sure not to lose any important information.

    QUESTIONS:
    """
    PROMPT_QUESTIONS = PromptTemplate(template=prompt_template_questions, input_variables=["text"])

    refine_template_questions = ("""
    As an expert in creating practice questions, your task is to refine the existing questions based on the additional context provided.

    Existing Questions:
    {existing_answer}

    Additional Context:
    ------------
    {text}
    ------------

    Instructions:
    - Carefully review the existing questions and the additional context.
    - Identify areas where the questions can be improved, clarified, or made more specific.
    - Consider the relevance, clarity, and difficulty level of each question.
    - Refine the questions to better align with the learning objectives and the provided context.
    - If a question is already well-formulated and relevant, you may keep it as is.
    - If the additional context is not helpful for a particular question, provide the original question.

    Refined Questions:
    """
    )
    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template_questions,
    )

    question_chain = load_summarize_chain(llm=llm, chain_type=chain_type, question_prompt=PROMPT_QUESTIONS, refine_prompt=REFINE_PROMPT_QUESTIONS, verbose=True)
    questions = question_chain.run(documents)
    return questions

def create_retrieval_qa_chain(documents: List[Document], llm: ChatOpenAI) -> RetrievalQA:
    embeddings = OpenAIEmbeddings()
    vector_database = Chroma.from_documents(documents=documents, embedding=embeddings)
    retrieval_qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_database.as_retriever())
    return retrieval_qa_chain


def init_session_state():
    if 'questions' not in st.session_state:
        st.session_state['questions'] = 'empty'
        st.session_state['questions_list'] = 'empty'
        st.session_state['questions_to_answer'] = 'empty'
        st.session_state['submitted'] = 'empty'


def run_app():
    st.title("Smart Quiz: Learning Companion")
    init_session_state()

    uploaded_file = st.file_uploader(label="Upload study material", type=['pdf'])

    if uploaded_file:
        text_from_pdf = load_data(uploaded_file)

        documents_for_question_gen = split_text(text=text_from_pdf, chunk_size=10000, chunk_overlap=200)
        documents_for_question_answer = split_text(text=text_from_pdf, chunk_size=1000, chunk_overlap=100)

        llm_question_gen = initialize_llm(model="gpt-3.5-turbo-16k", temperature=0.5)
        llm_question_answer = initialize_llm(model="gpt-3.5-turbo-16k", temperature=0)

        if st.session_state['questions'] == 'empty':
            with st.spinner("Generating questions..."):
                st.session_state['questions'] = generate_questions(llm=llm_question_answer, chain_type="refine", documents=documents_for_question_gen)

        if st.session_state['questions'] != 'empty':
            st.info(st.session_state['questions'])

            st.session_state['questions_list'] = st.session_state['questions'].split('\n')

            with st.form(key='my_form'):
                st.session_state['questions_to_answer'] = st.multiselect(label="Select questions to answer", options=st.session_state['questions_list'])

                submitted = st.form_submit_button("Generate Answer")

                if submitted:
                    st.session_state['submitted'] = True

            if st.session_state['submitted']:
                with st.spinner("Generating answers..."):
                    generate_answer_chain = create_retrieval_qa_chain(documents=documents_for_question_answer, llm=llm_question_answer)

                    for question in st.session_state['questions_to_answer']:
                        answer = generate_answer_chain.run(question)

                        st.write(f"Question: {question}")
                        st.info(f"Answer: {answer}")


if __name__ == "__main__":
    run_app()