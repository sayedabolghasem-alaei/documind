
import { useRef, useState } from "react";
import { uploadDocument } from "../services/api";

function DocumentUpload({
  onUploadSuccess,
  conversationId = null
}) {
  const fileInputRef = useRef(null);

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");
    setSuccess("");

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain",
    ];

    const allowedExtensions = [".pdf", ".docx", ".txt"];

    const fileExtension = file.name
      .slice(file.name.lastIndexOf("."))
      .toLowerCase();

    if (
      !allowedTypes.includes(file.type) &&
      !allowedExtensions.includes(fileExtension)
    ) {
      setError("Only PDF, DOCX and TXT files are supported.");
      event.target.value = "";
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError("File size must be less than 20 MB.");
      event.target.value = "";
      return;
    }

    try {
      setIsUploading(true);

      const response = await uploadDocument(
        file,
        conversationId
      );

      setSuccess(
        response.message || "Document uploaded successfully."
      );

      if (onUploadSuccess) {
        await onUploadSuccess(response);
      }

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Document upload failed."
      );

    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="document-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        hidden
      />

      <button
        type="button"
        className="upload-button"
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
      >
        {isUploading ? "Uploading..." : "+ Upload Document"}
      </button>

      {error && (
        <p className="upload-error">{error}</p>
      )}

      {success && (
        <p className="upload-success">{success}</p>
      )}
    </div>
  );
}

export default DocumentUpload;
