import streamlit as st
from openai import OpenAI
import PyMuPDF  # This is the library for reading PDFs

# Set the title and description
st.title("HW 1")
st.write("This app allows you to upload a .pdf or .txt document and ask a question about it.")

# Get OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
else:
    client = OpenAI(api_key=openai_api_key)

    # Function to read PDF files
    def read_pdf(file):
        with PyMuPDF.open(stream=file.getvalue(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text

    # Handle file upload
    uploaded_file = st.file_uploader(
        "Upload a document (.pdf or .txt)",
        type=["pdf", "txt"],
        help="Only .pdf and .txt files are supported."
    )

    document = None
    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == 'txt':
            document = uploaded_file.read().decode()
        elif file_extension == 'pdf':
            try:
                document = read_pdf(uploaded_file)
            except Exception as e:
                st.error(f"Error reading PDF file: {e}")
                document = None
        else:
            st.error("Unsupported file type. Please upload a .pdf or .txt file.")
    elif 'document' in st.session_state:
        # Clear the document from state if the file is removed from the UI
        del st.session_state.document
        st.write("File has been removed.")

    # Store the document in session state to handle UI changes
    if document:
        st.session_state.document = document

    # Get user question
    question = st.text_area(
        "Ask a question about the document!",
        placeholder="e.g., Can you give me a short summary?",
        disabled=not (uploaded_file or ('document' in st.session_state))
    )

    if uploaded_file and question:
        if 'document' in st.session_state:
            document_content = st.session_state.document
            messages = [
                {
                    "role": "user",
                    "content": f"Here's a document: {document_content} \n\n---\n\n {question}",
                }
            ]

            # Generate and stream the response
            stream = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                stream=True,
            )
            st.write_stream(stream)