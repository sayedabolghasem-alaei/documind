
import { useEffect, useState } from "react";
import { getDocuments } from "../services/api";

function DocumentList({ refreshKey = 0 }) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      setError("");

      const response = await getDocuments();

      setDocuments(response.documents || []);
    } catch (err) {
      setError(err.message || "Could not load documents.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, [refreshKey]);

  if (isLoading) {
    return (
      <div className="document-list">
        <p>Loading documents...</p>
      </div>
    );
  }

  return (
    <div className="document-list">
      <div className="document-list-header">
        <h3>My Documents</h3>
        <span>{documents.length} files</span>
      </div>

      {error && (
        <p className="document-error">{error}</p>
      )}

      {!error && documents.length === 0 && (
        <p className="empty-documents">
          No documents uploaded yet.
        </p>
      )}

      {documents.map((document, index) => (
        <div
          className="document-item"
          key={`${document.filename}-${index}`}
        >
          <div className="document-icon">📄</div>

          <div className="document-info">
            <strong>{document.filename}</strong>

            <span>
              {document.file_type?.toUpperCase() || "FILE"}
              {" · "}
              {document.total_chunks ?? 0} chunks
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default DocumentList;
