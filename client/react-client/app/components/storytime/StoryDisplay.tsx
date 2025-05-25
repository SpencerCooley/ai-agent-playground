import { FC, useState } from 'react';
import styles from '../../storytime/storytime.module.scss';
import ApiService from '../../services/api';

interface Character {
  name: string;
  personality_traits: string;
  image_description: string;
  image_url?: string;
}

interface Page {
  text: string;
  illustration: string;
}

interface StoryData {
  title: string;
  plot_summary: string;
  cover_image_description: string;
  characters: Character[];
  pages: Page[];
}

interface StoryDisplayProps {
  storyData: {
    plan: StoryData;
  };
}

const CharacterCard: FC<{ character: Character, index: number }> = ({ character, index }) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const apiService = new ApiService();

  const handleGenerateImage = async () => {
    try {
      setIsGenerating(true);
      const response = await apiService.generateImage({
        description: character.image_description,
        style: "children's book illustration, colorful, detailed"
      });
      setImageUrl(response.image_url);
      setIsGenerating(false);
    } catch (error) {
      console.error("Error generating image:", error);
      setIsGenerating(false);
    }
  };

  return (
    <div key={index} className={styles.characterListItems}>
      <h3>{character.name}</h3>
      
      {imageUrl && (
        <div className={styles.characterImage}>
          <img 
            src={`data:image/png;base64,${imageUrl}`} 
            alt={character.name} 
          />
        </div>
      )}
      
      <h4>Personality Traits</h4>
      <p>{character.personality_traits}</p>
      
      <h4>Image Description</h4>
      <p>{character.image_description}</p>
      {!imageUrl && (
        <button 
          onClick={handleGenerateImage} 
          className={styles.generateImageButton}
          disabled={isGenerating}
        >
          {isGenerating ? 'Generating...' : 'Generate Image'}
        </button>
      )}
    </div>
  );
};

const StoryDisplay: FC<StoryDisplayProps> = ({ storyData }) => {
  const { plan } = storyData;
  
  return (
    <div className={styles.story}>
      <h1>{plan.title}</h1>
      <h2>Summary:</h2>
      <p>{plan.plot_summary || "Something went wrong. Please try again."}</p>
      
      <h2>Characters:</h2>
      <div className={styles.characterWrap}>
        {plan.characters.map((character, index) => (
          <CharacterCard key={index} character={character} index={index} />
        ))}
      </div>
      
      <h2>Pages:</h2>
      {plan.pages.map((page, index) => (
        <div key={index} className={styles.page}>
          <h4>Page {index + 1}</h4>
          <p>{page.text}</p>
          <h4>Illustration Description</h4>
          <p>{page.illustration}</p>
        </div>
      ))}
    </div>
  );
};

export default StoryDisplay; 