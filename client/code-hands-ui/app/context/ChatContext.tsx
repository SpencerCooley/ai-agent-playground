"use client";

import React, { createContext, useContext, useState, ReactNode, JSX } from "react";

interface ChatContextType {
  taskId: string | null;
  setTaskId: (taskId: string | null) => void;
  response: string;
  setResponse: (response: string) => void;
  error: string | null;
  setError: (error: string | null) => void;
  isComplete: boolean;
  setIsComplete: (isComplete: boolean) => void;
}

const ChatContext = createContext<ChatContextType>({
  taskId: null,
  setTaskId: () => {},
  response: "",
  setResponse: () => {},
  error: null,
  setError: () => {},
  isComplete: false,
  setIsComplete: () => {},
});

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps): JSX.Element => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [response, setResponse] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState<boolean>(false);

  return (
    <ChatContext.Provider 
      value={{
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
}; 