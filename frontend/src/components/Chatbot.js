import React from "react";
import "./chatbot.css"; // Import CSS

function Chatbot({ question, setQuestion, onSubmit, chatHistory }) {
  return (
    <div className="chatbot-container">
      <div className="chat-window">
        <div className="messages">
          {chatHistory.map((entry, index) => (
            <div key={index} className="chat-message">
              <p className="user-message">You: {entry.question}</p>
              <p className="bot-message">Bot: {entry.answer}</p>
            </div>
          ))}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question"
            className="chat-input"
          />
          <button onClick={onSubmit} className="ask-button">
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
