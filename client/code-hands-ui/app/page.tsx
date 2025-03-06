'use client';

import styles from './page.module.scss';
import PromptBox from './components/PromptBox';
import StreamingResponse from './components/StreamingResponse';
import { useChat } from './context/ChatContext';
import { useTheme } from './context/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import { useEffect } from 'react';
import ApiService from './services/api';

export default function Home() {
  const { 
    prompt, 
    setTaskId, 
    setResponse, 
    setError, 
    setIsComplete 
  } = useChat();
  const { theme } = useTheme();

  useEffect(() => {
    if (!prompt) return;

    let ws;

    const handlePrompt = async () => {
      try {
        // Make initial API call
        const response = await ApiService.submitPrompt({ prompt });
        const taskId = response.task_id;
        console.log('Task ID received:', taskId);
        setTaskId(taskId);

        // Set up WebSocket connection
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL 
          ? `${process.env.NEXT_PUBLIC_WS_URL}/ws/${taskId}`
          : `ws://localhost:8000/prompt/ws/${taskId}`;
        console.log('Connecting to WebSocket URL:', wsUrl);
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log(`WebSocket connected for channel ${taskId}`);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('WebSocket message:', data);
          if (data.type === 'token') {
            setResponse(prevResponse => prevResponse + data.content);
          } else if (data.type === 'complete') {
            setIsComplete(true);
            ws.close();
          } else if (data.type === 'error') {
            setError(data.content);
            ws.close();
          }
        };

        ws.onerror = (error) => {
          setError('WebSocket error occurred');
          console.error('WebSocket error details:', error);
          console.error('WebSocket state:', ws.readyState);
          console.error('WebSocket URL:', ws.url);
          fetch('http://localhost:8000')
            .then(res => console.log('HTTP test response:', res.status))
            .catch(err => console.error('HTTP test failed:', err));
        };

        ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
        };
      } catch (error) {
        setError(`Failed to process prompt: ${error.message}`);
        console.error('HandlePrompt error:', error);
      }
    };

    handlePrompt().catch(err => {
      console.error('Unhandled promise rejection in handlePrompt:', err);
      setError(`Unhandled error: ${err.message}`);
    });

    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [prompt, setTaskId, setResponse, setError, setIsComplete]);

  return (
    <div className={`${styles.container} ${theme === 'dark' ? styles.darkTheme : ''}`}>
      <div className={styles.themeToggleWrapper}>
        <ThemeToggle />
      </div>
      <div className={styles.responseArea}>
        {prompt && <StreamingResponse />}
      </div>
      <div className={styles.promptBoxWrapper}>
        <PromptBox />
      </div>
    </div>
  );
}