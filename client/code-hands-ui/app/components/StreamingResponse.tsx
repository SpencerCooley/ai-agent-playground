'use client';

import { useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import styles from './StreamingResponse.module.scss';

export default function StreamingResponse() {
  const { 
    taskId,
    response,
    setResponse,
    error,
    setError,
    isComplete,
    setIsComplete
  } = useChat();

  useEffect(() => {
    if (!taskId) return;

    const ws = new WebSocket(`ws://localhost:8000/prompt/ws/${taskId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'error') {
        setError(data.content);
      } else if (data.type === 'token') {
        setResponse((prev: string) => prev + data.content);
      } else if (data.type === 'complete') {
        setIsComplete(true);
      }
    };

    ws.onerror = () => {
      setError('WebSocket error occurred');
    };

    return () => {
      ws.close();
    };
  }, [taskId, setResponse, setError, setIsComplete]);

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.response}>
      {response}
      {!isComplete && <span className={styles.cursor}>▋</span>}
    </div>
  );
} 