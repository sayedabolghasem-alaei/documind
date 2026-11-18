
import { useState, useEffect } from "react";

import {
    sendMessage,
    getConversations,
    createConversation,
    getConversation,
    renameConversation,
    deleteConversation,
} from "../services/api";


function useChat() {

    const [messages, setMessages] = useState([]);
    const [conversations, setConversations] = useState([]);
    const [conversationId, setConversationId] = useState(null);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);


    // Load all conversations.
    async function loadConversations() {

        try {
            const data = await getConversations();

            setConversations(data);

            return data;

        } catch (err) {
            setError(err.message);
            return [];
        }
    }


    // Load conversations when the application starts.
    useEffect(() => {

        async function initializeChat() {

            const data = await loadConversations();

            if (data.length > 0) {
                await selectConversation(data[0].id);
            }
        }

        initializeChat();

    }, []);


    // Select and load a conversation.
    async function selectConversation(id) {

        try {
            setIsLoading(true);
            setError(null);

            const data = await getConversation(id);

            setConversationId(data.id);

            setMessages(
                data.messages.map((message) => ({
                    id: message.id,
                    role: message.role,
                    content: message.content,
                    sources: [],
                }))
            );

        } catch (err) {
            setError(err.message);

        } finally {
            setIsLoading(false);
        }
    }


    // Create a new conversation.
    async function startNewChat() {

        try {
            setError(null);

            const conversation = await createConversation();

            setConversationId(conversation.id);
            setMessages([]);

            await loadConversations();

        } catch (err) {
            setError(err.message);
        }
    }


    // Send a message.
    async function handleSendMessage(query) {

        const trimmedQuery = query.trim();

        if (!trimmedQuery || isLoading) {
            return;
        }

        const userMessage = {
            id: crypto.randomUUID(),
            role: "user",
            content: trimmedQuery,
            sources: [],
        };

        setMessages((previous) => [
            ...previous,
            userMessage,
        ]);

        setIsLoading(true);
        setError(null);

        try {

            const response = await sendMessage(
                trimmedQuery,
                conversationId
            );

            const assistantMessage = {
                id: crypto.randomUUID(),
                role: "assistant",
                content: response.answer,
                sources: response.sources || [],
            };

            setMessages((previous) => [
                ...previous,
                assistantMessage,
            ]);

            if (response.conversation_id) {
                setConversationId(response.conversation_id);
            }

            await loadConversations();

        } catch (err) {

            setError(err.message || "Something went wrong.");

            setMessages((previous) => [
                ...previous,
                {
                    id: crypto.randomUUID(),
                    role: "assistant",
                    content: "Sorry, I couldn't process your request.",
                    sources: [],
                    isError: true,
                },
            ]);

        } finally {
            setIsLoading(false);
        }
    }


    // Rename a conversation.
    async function renameChat(id, title) {

        try {
            await renameConversation(id, title);
            await loadConversations();

        } catch (err) {
            setError(err.message);
        }
    }


    // Delete a conversation.
    async function removeConversation(id) {

        try {

            await deleteConversation(id);

            if (conversationId === id) {
                setConversationId(null);
                setMessages([]);
            }

            await loadConversations();

        } catch (err) {
            setError(err.message);
        }
    }


    return {
        messages,
        conversations,
        conversationId,
        isLoading,
        error,

        handleSendMessage,
        startNewChat,
        selectConversation,
        renameChat,
        removeConversation,
        loadConversations,
    };
}


export default useChat;
