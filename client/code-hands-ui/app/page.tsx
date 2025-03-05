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

    const handlePrompt = async () => {
      try {
        // Make initial API call
        const response = await ApiService.submitPrompt({ prompt });
        const taskId = response.task_id;
        setTaskId(taskId);

        // Set up WebSocket connection
        const ws = new WebSocket(`ws://your-websocket-url/${taskId}`);

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          setResponse(prevResponse => prevResponse + data.content);
          
          if (data.is_complete) {
            setIsComplete(true);
            ws.close();
          }
        };

        ws.onerror = (error) => {
          setError('WebSocket error occurred');
          console.error('WebSocket error:', error);
        };

        // Clean up WebSocket connection
        return () => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
        };
      } catch (error) {
        setError('Failed to process prompt');
        console.error('Error:', error);
      }
    };

    handlePrompt();
  }, [prompt, setTaskId, setResponse, setError, setIsComplete]);

  return (
    <div className={`${styles.container} ${theme === 'dark' ? styles.darkTheme : ''}`}>
      <div className={styles.themeToggleWrapper}>
        <ThemeToggle/>
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
