"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode, JSX } from "react";

// Define the type for the context value
interface ThemeContextType {
  theme: string;
  toggleTheme: () => void;
}

// Create context with a default value (remove null)
const ThemeContext = createContext<ThemeContextType>({
  theme: "dark",
  toggleTheme: () => {}
});

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

// Props type for the provider
interface ThemeProviderProps {
  children: ReactNode;
}

// Define the ThemeProvider component with JSX.Element as the return type
export const ThemeProvider = ({ children }: ThemeProviderProps): JSX.Element => {
  const [theme, setTheme] = useState<string>("dark");

  // Load theme from localStorage (persists across page reloads)
  useEffect(() => {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme) {
      setTheme(storedTheme);
      document.documentElement.className = storedTheme; // Sync DOM immediately
    } else {
      document.documentElement.className = "dark"; // Set default "dark" in DOM
    }
  }, []);
  
  // Update theme and save to localStorage
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.className = newTheme; // Update root element class
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
