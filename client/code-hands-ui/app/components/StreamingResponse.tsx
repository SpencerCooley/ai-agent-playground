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
  
  const handleWsMessages = (ws: WebSocket) => {
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', {
        timestamp: new Date().toISOString(),
        type: data.type,
        content: data.content
      });

      if (data.type === 'error') {
        setError(data.content);
      } else if (data.type === 'token') {
        console.log('Token received:', data.content);
        setResponse((prev: string) => prev + data.content);
      } else if (data.type === 'complete') {
        console.log('Stream complete');
        setIsComplete(true);
      }
    }
  }

  // when a new token id is set start the response stream
  useEffect(() => {
    if (!taskId) return;

    console.log('Connecting to WebSocket...');
    const ws = new WebSocket(`ws://localhost:8000/prompt/ws/${taskId}`);

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    handleWsMessages(ws);

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket error occurred');
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
    };

    return () => {
      console.log('Cleaning up WebSocket connection');
      ws.close();
    };
  }, [taskId]);

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