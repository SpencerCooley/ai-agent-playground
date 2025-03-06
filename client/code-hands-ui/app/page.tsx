'use client';

import styles from './page.module.scss';
import PromptBox from './components/PromptBox';
import StreamingResponse from './components/StreamingResponse';
import { useChat } from './context/ChatContext';
import { useTheme } from './context/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import ApiService from './services/api';
import { useEffect } from 'react';

let globalWs: WebSocket | null = null;

export default function Home() {
  const { 
    prompt, 
    taskId,
    setTaskId, 
    setResponse, 
    setError, 
    setIsComplete 
  } = useChat();
  const { theme } = useTheme();
  
  // changeing the prompt will set the task id.
  useEffect(() => {
    if (!prompt) return;

    const initiatePrompt = async () => {
      try {
        const response = await ApiService.submitPrompt({ prompt });
        setTaskId(response.task_id);
      } catch (error) {
        setError(`Failed to process prompt: ${error.message}`);
        console.error('InitiatePrompt error:', error);
      }
    };

    initiatePrompt();
  }, [prompt, setTaskId, setError]);

  // logging the task id to the console.
  useEffect(() => {
    console.log("Task ID: ", taskId);
  },[taskId]);

  
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