import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThemeProvider } from './components/ThemeContext';
import LoginPage from './components/pages/LoginPage';
import RoleSelectionModal from './components/RoleSelectionModal';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import HomePage from './components/pages/HomePage';
import ChatPage from './components/pages/ChatPage';
import VisualizationsPage from './components/pages/VisualizationsPage';
import DownloadDataPage from './components/pages/DownloadDataPage';
import SettingsPage from './components/pages/SettingsPage';
import TrendAnalysisPage from './components/pages/TrendAnalysisPage';
import { Toaster } from './components/ui/sonner';
import { auth, logout, updateUserRole, db } from './utils/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';

export default function App() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [language, setLanguage] = useState('en');
  const [showRoleModal, setShowRoleModal] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (authUser) => {
      if (authUser) {
        // Fetch user data from Firestore to get the correct role
        const userDocRef = doc(db, "users", authUser.uid);
        const userDocSnap = await getDoc(userDocRef);
        const userData = userDocSnap.exists() ? userDocSnap.data() : null;

        if (userData) {
          setUser({
            uid: authUser.uid,
            name: authUser.displayName || userData.name,
            email: authUser.email,
            role: userData.role,
          });

          // MODIFIED: Show role modal only if the role is not set
          if (!userData.role) {
            setShowRoleModal(true);
          }
        } else {
            // This case might happen for a brief moment if Firestore is slow
            // You can handle it by setting a loading state if you want
        }
      } else {
        setUser(null);
      }
    });

    return () => unsubscribe();
  }, []);

  const handleLogin = () => {
    // MODIFIED: The onAuthStateChanged listener now handles setting the user and showing the modal
    // This function will just handle navigation after login is initiated
    setCurrentPage('home');
  };
  
  const handleRoleSelection = async (role) => {
    if (user && user.uid && role) {
      try {
        // Update the role in the database
        await updateUserRole(user.uid, role);
        // Update the role in the application state
        setUser(prev => ({ ...prev, role }));
        console.log("Role updated successfully in Firestore and state.");
      } catch (error) {
        console.error("Error setting role:", error);
      }
    }
    setShowRoleModal(false);
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
    setCurrentPage('home');
  };

  const handleNavigation = (page) => setCurrentPage(page);

  const renderPage = () => {
    switch (currentPage) {
      case 'home': return <HomePage onNavigate={handleNavigation} language={language} />;
      case 'chat': return <ChatPage user={user} language={language} />;
      case 'visualizations': return <VisualizationsPage user={user} language={language} />;
      case 'download': return <DownloadDataPage user={user} language={language} />;
      case 'settings': return <SettingsPage user={user} setUser={setUser} language={language} />;
      case 'trends': return <TrendAnalysisPage user={user} language={language} />;
      default: return <HomePage onNavigate={handleNavigation} language={language} />;
    }
  };

  if (!user) {
    return (
      <ThemeProvider>
        <LoginPage onLogin={handleLogin} />
        <Toaster />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      {showRoleModal && (
        <RoleSelectionModal isOpen={showRoleModal} onRoleSelect={handleRoleSelection} />
      )}
      <div className="flex h-screen bg-muted/40">
        <Sidebar
          isOpen={sidebarOpen}
          currentPage={currentPage}
          onNavigate={handleNavigation}
          language={language}
        />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header
            user={user}
            onLogout={handleLogout}
            setSidebarOpen={setSidebarOpen}
            language={language}
            setLanguage={setLanguage}
          />
          <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                {renderPage()}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>
      <Toaster />
    </ThemeProvider>
  );
}