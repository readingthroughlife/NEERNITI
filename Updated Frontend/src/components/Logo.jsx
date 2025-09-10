import React from 'react';
import { useTheme } from './ThemeContext';
import { Droplets, Leaf, Waves } from 'lucide-react';

const Logo = () => {
  const { theme } = useTheme();

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <Droplets className={theme === 'dark' ? 'text-white' : 'text-blue-900'} size={28} />
        <Leaf className="absolute -top-1 -right-1 text-teal-500" size={16} />
        <Waves className="absolute bottom-0 right-0 text-blue-500" size={12} />
      </div>
      <span className="text-xl font-bold text-gray-900 dark:text-white">NeerNiti</span>
    </div>
  );
};

export default Logo;