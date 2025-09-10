import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  return (
    <footer className="bg-white dark:bg-gray-800 border-t dark:border-gray-700 p-4 text-center text-sm text-gray-500 dark:text-gray-400 mt-auto">
      © {currentYear} NeerNiti • Powered by Hacktopus
    </footer>
  );
};

export default Footer;