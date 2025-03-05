"use client";
import { useTheme } from "../context/ThemeContext"; // Adjust the path as needed
import styles from "./PromptBox.module.scss";
import { useState, ChangeEvent, KeyboardEvent } from "react";
import { useChat } from '../context/ChatContext';
import ApiService from '../services/api';

export default function PromptBox() {
    const { theme } = useTheme(); 
    const { setPrompt } = useChat();
    const [inputValue, setInputValue] = useState<string>("");

    const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setInputValue(e.target.value);
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) { 
            e.preventDefault(); 
            setPrompt(inputValue);
            setInputValue(""); 
        }
    };

    return (
        <div className={`${styles.promptBoxContainer} ${theme}`}>
            <textarea
                value={inputValue}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                className={styles.promptBox}
                placeholder="Type here and press Enter..."
            />
        </div>
    );
}
