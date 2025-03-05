"use client";

import React, { createContext, useContext, useState, ReactNode, JSX } from "react";

interface ChatContextType {
  prompt: string;
  setPrompt: (prompt: string) => void;
  taskId: string;
  setTaskId: (id: string) => void;
  response: string;
  setResponse: (response: string) => void;
  error: string | null;
  setError: (error: string | null) => void;
  isComplete: boolean;
  setIsComplete: (isComplete: boolean) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [prompt, setPrompt] = useState<string>('');
  const [taskId, setTaskId] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState<boolean>(false);

  return (
    <ChatContext.Provider
      value={{
        prompt,
        setPrompt,
        taskId,
        setTaskId,
        response,
        setResponse,
        error,
        setError,
        isComplete,
        setIsComplete,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
} 