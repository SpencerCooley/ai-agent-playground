import { FC, ChangeEvent } from 'react';
import styles from '../../storytime/storytime.module.scss';

interface StoryFormProps {
  prompt: string;
  onPromptChange: (e: ChangeEvent<HTMLTextAreaElement>) => void;
  onGenerate: () => void;
}

const StoryForm: FC<StoryFormProps> = ({ prompt, onPromptChange, onGenerate }) => {
  return (
    <>
      <h1>Generate a story</h1>
      <p>Enter a prompt to generate a story.</p>
      <textarea 
        onChange={onPromptChange} 
        value={prompt}
        className={styles.promptBox} 
        placeholder='Enter a prompt to generate a story.'
      />
      <button onClick={onGenerate} className={styles.generateButton}>
        Generate
      </button>
      <h2>Example Prompt</h2>
      <p>Create a captivating short story for children ages 8 to 12 about a frog named Freddy who must find a magic treasure to rescue his best friend, Lily, kidnapped by a cunning swarm of flies.</p>
    </>
  );
};

export default StoryForm; 