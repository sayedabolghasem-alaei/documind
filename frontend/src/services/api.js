
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

// Handle API responses and errors
async function handleResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      data.detail ||
      data.message ||
      `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data;
}

// Upload a document
export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  return handleResponse(response);
}

// Get all uploaded documents
export async function getDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/documents/`
  );

  return handleResponse(response);
}

// Send a question to the AI assistant
export async function sendMessage(query, conversationId = null) {
  const response = await fetch(
    `${API_BASE_URL}/chat/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        conversation_id: conversationId,
      }),
    }
  );

  return handleResponse(response);
}
