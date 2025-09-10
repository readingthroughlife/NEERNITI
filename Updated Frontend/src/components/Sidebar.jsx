import React from 'react';
import { motion } from 'framer-motion';
import { Button } from './ui/Button';
import { Separator } from './ui/Separator';
import { Home, MessageSquare, BarChart3, Download, Settings, TrendingUp } from 'lucide-react';
import { translations } from './i18n';

const Sidebar = ({ isOpen, currentPage, onNavigate, language }) => {
  const t = translations[language];

  const mainNav = [
    { id: 'home', label: t.home, icon: Home },
    { id: 'chat', label: t.chat, icon: MessageSquare },
    { id: 'visualizations', label: t.visualizations, icon: BarChart3 },
    { id: 'settings', label: t.settings, icon: Settings },
  ];

  const quickActions = [
    { id: 'download', label: t.downloadData, icon: Download },
    { id: 'trends', label: t.trendAnalysis, icon: TrendingUp },
  ];

  return (
    <motion.aside
      initial={false}
      animate={{ width: isOpen ? '280px' : '0px' }}
      className="bg-card border-r flex-shrink-0 overflow-hidden"
    >
      <div className="flex flex-col h-full w-[280px]">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold">{t.appName}</h1>
          <p className="text-sm text-muted-foreground">AI Assistant</p>
        </div>
        <div className="flex-1 p-4 space-y-2">
          {mainNav.map((item) => (
            <Button
              key={item.id}
              variant={currentPage === item.id ? 'secondary' : 'ghost'}
              className="w-full justify-start gap-3"
              onClick={() => onNavigate(item.id)}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Button>
          ))}
          <Separator className="my-4" />
          <h3 className="px-4 py-2 text-sm font-semibold text-muted-foreground">{t.quickActions}</h3>
          {quickActions.map((item) => (
            <Button
              key={item.id}
              variant="ghost"
              className="w-full justify-start gap-3"
              onClick={() => onNavigate(item.id)}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Button>
          ))}
        </div>
      </div>
    </motion.aside>
  );
};

export default Sidebar;