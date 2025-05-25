'use client';

import { useState, useEffect, ChangeEvent } from 'react';
import ThemeToggle from '../components/ThemeToggle';
import { useTheme } from '../context/ThemeContext';
import styles from './storytime.module.scss';
import ApiService from '../services/api';
import StoryDisplay from '../components/storytime/StoryDisplay';
import StoryForm from '../components/storytime/StoryForm';

export default function Home() {
    const { theme } = useTheme();

    const [prompt, setPrompt] = useState('');
    const [story, setStory] = useState<any>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const apiService = new ApiService();
    const defaultPromptRules = "The story should unfold naturally as a cohesive narrative, following a classic plot arc (exposition, rising action, climax, falling action, resolution) without explicitly labeling or separating these components in the text. Instead, the plot should be woven into a series of vivid, engaging scenes, like pages in a children's book, each telling a part of the protaganists adventure in simple, age-appropriate language. It is ok to include dialouge and detail in each page. The number of pages is flexible—use as many as needed to tell a compelling, heartfelt story. Include a variety of characters (animals, humans, or mystical creatures, aliens, etc.) to enrich the journey, ensuring they fit naturally into the narrative. Provide detailed image descriptions for each scene to capture the story's mood and setting. tell the story in a lighthearted, empathetic, and dramatic tone. Also make sure that you utilize the full range of emotions as is appropriate for the story, not just happy, but sad, angry, excited, etc."
    
    // this is the schema we want returned from the api
    const schema = {
        "plot_summary": "string",
        "title": "string for the title of the story",
        "cover_image_description": "string that describes what the cover of the book looks like",
        "characters": [
            { // a list of characters in the story with image descriptions
                "name":"string", "personality_traits": "string describing personality", 
                "image_description": "string describing in detail what this character looks like"
            }
        ],
        "pages": [
            { // a list of pages in the story with image descriptions
                "text": "string for the storytelling of the page", 
                "illustration": "string describing what the illustration for this section of the story"
            }
        ]
    }

    const handlePromptChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setPrompt(e.target.value);
    };

    const handleGenerate = async () => {
        try {
            setIsGenerating(true);
            const response = await apiService.generatePlan({
                intent: prompt+` ${defaultPromptRules}`,
                plan_type: 'story',
                schema: schema
            });

            setStory(response);
            setIsGenerating(false);
        } catch (error) {
            console.error("Error generating story:", error);
            setIsGenerating(false);
        }
    }

    useEffect(() => {
        console.log(story);
    }, [story]);
    
    return (
        <div className={`${styles.container} ${theme === 'dark' ? styles.darkTheme : ''}`}>
            {isGenerating && <div className={styles.generatingOverlay}></div>}    
                <div className={styles.themeToggleWrapper}>
                    <ThemeToggle />
                </div>
                <div className={styles.content}>
                    {!story ? (
                        <StoryForm 
                            prompt={prompt}
                            onPromptChange={handlePromptChange}
                            onGenerate={handleGenerate}
                        />
                    ) : (
                        <StoryDisplay storyData={story} />
                    )}
                    
                </div>
        </div>
    );
}