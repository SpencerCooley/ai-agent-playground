'use client';

import styles from './page.module.scss';
import PromptBox from './components/PromptBox';
import StreamingResponse from './components/StreamingResponse';
import { useChat } from './context/ChatContext';
import { useTheme } from './context/ThemeContext';

export default function Home() {
  const { taskId } = useChat();
  const { theme } = useTheme();

  return (
    <div className={`${styles.container} ${theme === 'dark' ? styles.darkTheme : ''}`}>
      <div className={styles.responseArea}>
        {taskId && <StreamingResponse />}
      </div>
      <div className={styles.promptBoxWrapper}>
        <PromptBox />
      </div>
    </div>
  );
}
