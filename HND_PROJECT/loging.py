from dotenv import load_dotenv
import streamlit as st
from streamlit_option_menu import option_menu
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

if not firebase_admin._apps:
    cred = credentials.Certificate("langchain-pdf-reader-51b106fd5fc6.json")
    default_app = firebase_admin.initialize_app(cred )

def main():
    load_dotenv()
          
          
    st.set_page_config(
      page_title="STECHCO",
      page_icon="📚",
      )
    # sidebar content
    with st.sidebar:
      
      st.title('STECHCO📚 Chat App')
      st.text('')
      st.markdown('''
                   
                  ''')
        
    page_bg_img = """
    <style>
    [data-testid="stApp"] {
        background-image: url("https://webusupload.apowersoft.info/lightpdf/wp-content/uploads/2022/05/turn-pdf-to-darkmode.jpg.webp");
        background-size: cover;
        
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0);
    }
    
    [data-testid="stToolbar"] {
        background-color: rgba(255, 255, 255, 0);
        right: 2rem;
    }
    
    [data-testid="stMainMenu"]:hover {
        border-radius: 5rem;
        background-color: rgb(255, 1, 1);
        color: rgba(5, 44, 44);
    }
    
    [data-testid="collapsedControl"] {
        background-color: rgba(255, 255, 255, 0);
    }
    
    [data-testid="baseButton-headerNoPadding"] {
        background-color: rgb(111, 178, 241);;
      }
    
    [data-testid="baseButton-header"] {
        display: inline-block;
        cursor: pointer;
        padding: 1rem;
        border: rgb(255, 1, 1);
        font-size: 15px;
        color: rgb(255, 255, 255,);
        text-align: center;
        text-transform: capitalize;
        transition: .2s linear;
    }
    
    [data-testid="textInputRootElement"] {
        height: 40px;
        width: 95%;
        border-radius: 7px;
        outline: none;
        border: 1px solid #808080;
        padding: 0 10px;
    }
    [data-testid="stWidgetLabel"] {
        height: 40px;
        width: 95%;
        border-radius: 7px;
        outline: none;
        border: 0px solid #808080;
        padding: 0 10px;
        margin-right: 20px;
    }
    
    [data-testid="stMarkdownContainer"] {
        margin-left: 20px;
    }
    
    
    [data-testid="baseButton-header"]:hover{
    border-radius: 5rem;
    background-color: rgb(255, 1, 1);
    color: rgba(5, 44, 44);
    }
    [data-testid="stSidebar"] {
        background-color: rgb(83, 172, 255);;
        background-size: cover;
    }
    [data-testid="stButton"] {
        display: inline-block;
        cursor: pointer;
        padding: 1rem 3rem;
        font-size: 1.8rem;
        color: var(--sub-color);
        text-align: center;
        text-transform: capitalize;
        transition: .2s linear;
        margin-top: 1rem;
        margin: auto;
    }
    
    </style>
    """
      
    st.markdown(page_bg_img, unsafe_allow_html = True)
          
          
    st.title(':red[STECHCO]📚 chat app')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''



    def f(): 
        try:
            user = auth.get_user_by_email(email)
            print(user.uid)
            st.session_state.username = user.uid
            st.session_state.useremail = user.email
            
            global Usernm
            Usernm=(user.uid)
            
            st.session_state.signedout = True
            st.session_state.signout = True    
  
            
        except: 
            st.warning('Login Failed')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False   
        st.session_state.username = ''


        
    
        
    if "signedout"  not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False    
        

        
    
    if  not st.session_state["signedout"]: # only show if the state is False, hence the button has never been clicked
        choice = st.selectbox(':red[Login/Signup]',['Login','Sign up'])
        email = st.text_input(':red[Email Address]', placeholder= 'enter your email')
        password = st.text_input(':red[Password]', placeholder='enter your password',type='password')
        

        
        if choice == 'Sign up':
            username = st.text_input(":red[Enter  your unique username]",placeholder='Username' )
            
            if st.button('Create my account'):
                user = auth.create_user(email = email, password = password,uid=username)
                
                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')
                st.balloons()
        else:
            # st.button('Login', on_click=f)          
            st.button('Login', on_click=f)
            
            
    if st.session_state.signout:
                st.header('Welcome back '+st.session_state.username)
                # st.title(':red[STECHCO]📚 chat app')
                #st.write('Made by MOLACK FOTSO STEVE BRANLY')
                st.header("Ask your PDF 💬🌝")
                # upload file
                pdf = st.file_uploader("Upload your PDF", type="pdf")
                # extract the text
                if pdf is not None:
                    pdf_reader = PdfReader(pdf)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
        
                    # split into chunks
                    text_splitter = CharacterTextSplitter(
                        separator="\n",
                        chunk_size=1000,
                        chunk_overlap=200,
                        length_function=len
                    )
                    chunks = text_splitter.split_text(text)
      
                    # create embeddings
                    embeddings = OpenAIEmbeddings()
                    knowledge_base = FAISS.from_texts(chunks, embeddings)
      
                    # show user input
                    user_question = st.text_input("Ask a question about your PDF:")
                    if user_question:
                        docs = knowledge_base.similarity_search(user_question)
        
                        llm = OpenAI()
                        chain = load_qa_chain(llm, chain_type="stuff")
                        with get_openai_callback() as cb:
                            response = chain.run(input_documents=docs, question=user_question)
                            print(cb)
           
                        st.write(response)
                # st.text('Name '+st.session_state.username)
                # st.text('Email id: '+st.session_state.useremail)
                st.button('Sign out', on_click=t) 
    
    
    
    
   
    

if __name__ == '__main__':
    main()
