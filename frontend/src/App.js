import React, { useState } from "react";
import axios from "axios";
import "./App.css"; // Import the CSS file

function App() {
  const [file, setFile] = useState(null); // State to store the selected file
  const [question, setQuestion] = useState(""); // State to store the current question
  const [fileId, setFileId] = useState(""); // State to store the file ID from the backend
  const [chatHistory, setChatHistory] = useState([]); // State to store the chat history
  const [error, setError] = useState(""); // State to handle errors

  // Handle file selection
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      // Set the fileId from the response
      setFileId(response.data.file_id);
      setError("");
      alert("File uploaded successfully!");
    } catch (err) {
      setError(
        "Error uploading file: " + err.response?.data?.error || err.message
      );
    }
  };

  // Handle question submission
  const handleQuestionSubmit = async () => {
    if (!fileId) {
      setError("Please upload a PDF file before asking a question.");
      return;
    }
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5000/ask", {
        question: question,
        file_id: fileId,
      });

      // Update chat history with the new question and answer
      setChatHistory([
        ...chatHistory,
        { question: question, answer: response.data.answer },
      ]);

      // Clear the input field after the question is submitted
      setQuestion("");
      setError("");
    } catch (err) {
      setError(
        "Error asking question: " + err.response?.data?.error || err.message
      );
    }
  };

  return (
    <div className="app-container">
      <h1>PDF Chatbot</h1>

      {/* File Upload Section */}
      <div className="upload-section">
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload PDF</button>
      </div>

      {/* Chat History */}
      <div className="chat-history">
        {chatHistory.map((chat, index) => (
          <div key={index} className="chat-bubble">
            <p>
              <strong>Q:</strong> {chat.question}
            </p>
            <p>
              <strong>A:</strong> {chat.answer}
            </p>
          </div>
        ))}
      </div>

      {/* Question Submission Section */}
      <div className="input-section">
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="input-box"
        />
        <button onClick={handleQuestionSubmit}>Submit Question</button>
      </div>

      {/* Display Error */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}

export default App;
