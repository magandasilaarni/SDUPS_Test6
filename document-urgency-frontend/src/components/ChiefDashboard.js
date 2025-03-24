import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import moment from "moment";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

const ChiefDashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [previewError, setPreviewError] = useState(false);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/api/queue`);
        setDocuments(response.data);
        setError(null);
      } catch (error) {
        setError("Failed to load documents");
        console.error("Error fetching documents:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDocuments();
  }, []);

  const handleAction = async (doc, action) => {
    if (!action) {
      setError("Please select an action before submitting.");
      return;
    }
    setLoading(true);
    try {
      const updateData = {
        status: action === "approved" ? "Approved" : "Rejected",
        comments: comment,
      };
      await axios.patch(`${API_URL}/api/queue/${doc.id}`, updateData);
      setSelectedDoc(null);
      setComment("");
      const response = await axios.get(`${API_URL}/api/queue`);
      setDocuments(response.data);
    } catch (error) {
      console.error("Error updating document:", error);
      setError("Failed to process the action");
    } finally {
      setLoading(false);
    }
  };

  const toggleReview = (doc) => {
    if (selectedDoc && selectedDoc.id === doc.id) {
      setSelectedDoc(null);
    } else {
      setSelectedDoc(doc);
      setPreviewError(false);
    }
  };

  const handlePreviewError = () => {
    setPreviewError(true);
  };

  return (
    <div className="container mt-5">
      <h2>Chief Dashboard</h2>
      {loading && <p>Loading...</p>}
      {error && <div className="alert alert-danger">{error}</div>}

      <table className="table table-striped mt-3">
        <thead>
          <tr>
            <th>#</th>
            <th>Filename</th>
            <th>Urgency</th>
            <th>Upload Time</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
              <td>{doc.filename}</td>
              <td>{doc.urgency}</td>
              <td>{moment(doc.upload_time).format("MMMM Do YYYY, h:mm:ss a")}</td>
              <td>{doc.status}</td>
              <td>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => toggleReview(doc)}
                >
                  {selectedDoc && selectedDoc.id === doc.id ? "Close" : "Review"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedDoc && (
        <div className="mt-4 p-3 border rounded">
          <h3>Review Document: {selectedDoc.filename}</h3>

          <div className="form-group">
            <label>Action</label>
            <select
              className="form-control"
              onChange={(e) => setSelectedDoc({ ...selectedDoc, action: e.target.value })}
              value={selectedDoc.action || ""}
            >
              <option value="">Select Action</option>
              <option value="approved">Approve</option>
              <option value="rejected">Reject</option>
            </select>
          </div>

          <div className="form-group mt-2">
            <label>Comment</label>
            <textarea
              className="form-control"
              rows="3"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            ></textarea>
          </div>

          <button
            className="btn btn-success mt-3"
            onClick={() => handleAction(selectedDoc, selectedDoc.action)}
          >
            Submit
          </button>

          <div className="mt-3">
            <h4>Document Preview</h4>
            {previewError ? (
              <div className="alert alert-danger">Failed to load preview.</div>
            ) : (
              <iframe
                src={`${API_URL}/upload/${selectedDoc.filename}`}
                width="100%"
                height="500px"
                title="Document Preview"
                onError={handlePreviewError}
                className="border rounded"
              ></iframe>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

function reviewDocument(fileId) {
  const pdfViewer = document.getElementById("pdfViewer");
  pdfViewer.src = `/review/${fileId}`; // Load PDF into the viewer

  const modal = document.getElementById("pdfModal");
  modal.style.display = "block"; // Show modal
}

// Close the modal when clicking outside
window.onclick = function(event) {
  const modal = document.getElementById("pdfModal");
  if (event.target === modal) {
      modal.style.display = "none";
  }
};


export default ChiefDashboard;
