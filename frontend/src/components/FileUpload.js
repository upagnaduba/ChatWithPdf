import React from "react";
import "./fileupload.css";

function FileUpload({ onFileChange, onUpload, flag }) {
  return (
    <div className="file-upload-container">
      <input type="file" onChange={onFileChange} className="upload-input" />
      <button onClick={onUpload} className="upload-button">
        Upload
      </button>
      {flag && <p className="upload-status">{flag}</p>}
    </div>
  );
}

export default FileUpload;
