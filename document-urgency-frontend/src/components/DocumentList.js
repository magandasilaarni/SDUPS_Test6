import React from "react";

function DocumentList({ documents }) {
  return (
    <div>
      <h2>Document Queue</h2>
      <table>
        <thead>
          <tr>
            <th>Filename</th>
            <th>Urgency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className={doc.urgency === "Urgent" ? "urgent" : ""}>
              <td>{doc.filename}</td>
              <td>{doc.urgency}</td>
              <td>{doc.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DocumentList;
