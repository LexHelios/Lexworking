import React, { createContext, useContext } from 'react';

// Types
interface ThemeContextType {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

// Create context
export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Hook to use theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
};

export default ThemeContext;