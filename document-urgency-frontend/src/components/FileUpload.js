import React, { useState } from "react";
import axios from "axios";
import moment from "moment";

const FileUpload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [urgency, setUrgency] = useState("");
    const [uploadTime, setUploadTime] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            setMessage("Please select a PDF file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("uploaded_by", "John Doe");  // Replace with actual user data

        try {
            // Upload the file
            const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setUrgency(`Urgency: ${response.data.urgency}`);
            setMessage(response.data.message);
            setUploadTime(moment(response.data.upload_time));
            setSuccessMessage("File successfully uploaded!");
            onUploadSuccess();
        } catch (error) {
            console.error("Error uploading file:", error);
            if (error.response) {
                setMessage(`Upload failed: ${error.response.data.message}`);
            } else {
                setMessage("File upload failed: Network error or server is not responding.");
            }
        }
    };

    return (
        <div className="container mt-5">
            <div className="card shadow p-4">
                <h2>Upload a PDF Document</h2>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <input type="file" className="form-control" accept=".pdf" onChange={handleFileChange} />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={!file}>
                        Upload
                    </button>
                </form>
                {message && <div className="alert alert-info mt-3">{message}</div>}
                {urgency && <div className="alert alert-warning mt-3">{urgency}</div>}
                {uploadTime && (
                    <div className="alert alert-success mt-3">
                        Uploaded on: {uploadTime.format("MMMM Do YYYY, h:mm:ss a")}<br />
                        Time since upload: {uploadTime.fromNow()}
                    </div>
                )}
                {successMessage && <div className="alert alert-success mt-3">{successMessage}</div>}
            </div>
        </div>
    );
};

export default FileUpload;
