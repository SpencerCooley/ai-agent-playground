"use client";
import { useTheme } from "../context/ThemeContext"; // Adjust the path as needed
import styles from "./PromptBox.module.scss";
import { useState, ChangeEvent, KeyboardEvent } from "react";

export default function PromptBox() {
    const { theme, toggleTheme } = useTheme(); 
    const [prompt, setPrompt] = useState<string>("");

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
