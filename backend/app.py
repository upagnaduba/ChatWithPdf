from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['pdf_database']  # Create or use existing database
fs = gridfs.GridFS(db)  # Initialize GridFS

# Initialize the ChatGroq model
llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama-3.1-70b-versatile"
)

def extract_text_from_pdf(file_data):
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    
    :param file_data: File data in bytes.
    :return: Extracted text as a string.
    """
    text = ""
    try:
        with fitz.open(stream=file_data, filetype="pdf") as pdf:
            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise e
    return text

def process_text_with_llm(extracted_text, question):
    """
    Processes the extracted text and question using the ChatGroq LLM.
    
    :param extracted_text: Text extracted from the PDF.
    :param question: User's question.
    :return: Generated answer from the LLM.
    """
    try:
        prompt_template = PromptTemplate.from_template(
            """
            ### EXTRACTED TEXT:
            {extracted_text}

            ### QUESTION:
            {question}

            ### INSTRUCTION:
            Based on the extracted text above, please provide a detailed and accurate answer to the question.
            ### ANSWER:
            """
        )
        # Create the processing chain
        chain = prompt_template | llm
        # Invoke the chain with input
        response = chain.invoke(input={'extracted_text': extracted_text, 'question': question})
        return response.content
    except Exception as e:
        print(f"Error processing text with LLM: {e}")
        raise e

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file uploads. Only accepts PDF files.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading.'}), 400

    if file and file.filename.lower().endswith('.pdf'):
        try:
            # Save the PDF file to MongoDB using GridFS
            file_id = fs.put(file, filename=file.filename)
            print(f"File uploaded successfully to MongoDB with ID: {file_id}")
            return jsonify({'message': 'File uploaded successfully.', 'file_id': str(file_id)}), 200
        except Exception as e:
            print(f"Error saving file to MongoDB: {e}")
            return jsonify({'error': 'Failed to save the uploaded file to MongoDB.'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Handles questions by processing the uploaded PDF and generating an answer using LLM.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided.'}), 400

        question = data.get('question', '').strip()
        file_id = data.get('file_id', '').strip()

        if not question:
            return jsonify({'error': 'No question provided.'}), 400

        if not file_id:
            return jsonify({'error': 'No file ID provided.'}), 400

        # Retrieve the file from MongoDB GridFS
        try:
            file_data = fs.get(ObjectId(file_id)).read()
        except Exception as e:
            return jsonify({'error': f'Could not retrieve file with ID {file_id}.'}), 404

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(file_data)
        if not extracted_text.strip():
            return jsonify({'error': 'Failed to extract text from the uploaded PDF.'}), 500

        # Process the extracted text with LLM to answer the question
        answer = process_text_with_llm(extracted_text, question)
        if not answer:
            return jsonify({'error': 'LLM did not return a response.'}), 500

        return jsonify({'answer': answer}), 200

    except Exception as e:
        print(f"Error in /ask endpoint: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
