import React, { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import axios from "axios";
import moment from "moment";
import "./Dashboard.css";

const API_URL = "http://127.0.0.1:5000";

const Dashboard = forwardRef((props, ref) => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchFiles = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_URL}/api/queue`);
            console.log(response.data);  // Debugging output
            let documents = Array.isArray(response.data) ? response.data : [];
            
            // Debugging output for urgency scores
            documents.forEach(doc => {
                console.log(`Document: ${doc.filename}, Urgency Scores:`, doc.urgency_scores);
            });

            // Sort documents based on urgency
            documents.sort((a, b) => {
                const urgencyA = a.urgency_scores ? a.urgency_scores.high : 0;
                const urgencyB = b.urgency_scores ? b.urgency_scores.high : 0;
                return urgencyB - urgencyA;
            });

            setDocuments(documents);
            setError(null);
        } catch (err) {
            setError("Failed to fetch documents. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    useImperativeHandle(ref, () => ({
        fetchFiles,
    }));

    useEffect(() => {
        fetchFiles();
    }, []);

    return (
        <div className="dashboard-container">
            <h2>Smart Document Urgency Processing System</h2>
            
            <button className="refresh-btn" onClick={fetchFiles}>Refresh</button>

            <h3>Document Dashboard</h3>

            {loading ? (
                <p>Loading documents...</p>
            ) : error ? (
                <div className="error">{error}</div>
            ) : documents.length === 0 ? (
                <p>No files have been uploaded yet.</p>
            ) : (
                <table className="document-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Filename</th>
                            <th>Urgency</th>
                            <th>Uploaded On</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {documents.map((doc, index) => (
                            <tr key={doc.id || index}>
                                <td>{index + 1}</td>
                                <td>{doc.filename}</td>
                                <td>
                                    {doc.urgency_scores ? (
                                        <div className="urgency-bar">
                                            <div
                                                className="high"
                                                style={{ width: `${doc.urgency_scores.high * 100}%` }}
                                            ></div>
                                            <div
                                                className="medium"
                                                style={{ width: `${doc.urgency_scores.medium * 100}%` }}
                                            ></div>
                                            <div
                                                className="low"
                                                style={{ width: `${doc.urgency_scores.low * 100}%` }}
                                            ></div>
                                        </div>
                                    ) : (
                                        <p>{doc.urgency}</p>
                                    )}
                                </td>
                                <td>
                                    {moment(doc.upload_time).isValid()
                                        ? moment(doc.upload_time).format("MMMM Do YYYY, h:mm:ss a")
                                        : "Invalid Date"}
                                </td>
                                <td>{doc.status}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
});

export default Dashboard;