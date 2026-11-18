
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
export const uploadDocument = async (file, conversationId = null) => {
  const formData = new FormData();

  formData.append("file", file);

  if (conversationId) {
    formData.append("conversation_id", conversationId);
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  return handleResponse(response);
};

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

// ==============================
// Conversation APIs
// ==============================

export const getConversations = async () => {
    const response = await fetch(`${API_BASE_URL}/conversations/`);

    if (!response.ok) {
        throw new Error("Failed to fetch conversations.");
    }

    return response.json();
};


export const createConversation = async (title = "New Chat") => {
    const response = await fetch(`${API_BASE_URL}/conversations/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ title }),
    });

    if (!response.ok) {
        throw new Error("Failed to create conversation.");
    }

    return response.json();
};


export const getConversation = async (conversationId) => {
    const response = await fetch(
        `${API_BASE_URL}/conversations/${conversationId}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch conversation.");
    }

    return response.json();
};


export const renameConversation = async (conversationId, title) => {
    const response = await fetch(
        `${API_BASE_URL}/conversations/${conversationId}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title }),
        }
    );

    if (!response.ok) {
        throw new Error("Failed to rename conversation.");
    }

    return response.json();
};


export const deleteConversation = async (conversationId) => {
    const response = await fetch(
        `${API_BASE_URL}/conversations/${conversationId}`,
        {
            method: "DELETE",
        }
    );

    if (!response.ok) {
        throw new Error("Failed to delete conversation.");
    }

    return response.json();
};