"use client";
import { useTheme } from "../context/ThemeContext"; // Adjust the path as needed
import styles from "./PromptBox.module.scss";
import { useState, ChangeEvent, KeyboardEvent } from "react";
import { useChat } from '../context/ChatContext';
import ApiService from '../services/api';

export default function PromptBox() {
    const { theme, toggleTheme } = useTheme(); 
    const { setTaskId, setResponse, setError, setIsComplete } = useChat();
    const [prompt, setPrompt] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    // Handle textarea value change
    const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setPrompt(e.target.value);
    };

    // Handle Enter key press
    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) { 
            e.preventDefault(); 
            console.log("Enter pressed with value:", prompt);

            setPrompt(""); 
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        
        // Reset states for new submission
        setResponse('');
        setError(null);
        setIsComplete(false);

        try {
            const response = await ApiService.submitPrompt({ prompt });
            setTaskId(response.task_id);
        } catch (error) {
            setError('Failed to submit prompt');
            console.error('Error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={`${styles.promptBoxContainer} ${theme}`}>
            <textarea
                value={prompt}
                onChange={handleChange}
                onKeyDown={handleKeyDown} // Capture Enter key press
                className={styles.promptBox}
                placeholder="Type here and press Enter..."
            />
        </div>
    );
}
