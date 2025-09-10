import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '../ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { translations } from '../i18n';
import { Droplets, ShieldCheck, Recycle } from 'lucide-react';

const HomePage = ({ onNavigate, language }) => {
  const t = translations[language];

  const infoCards = [
    {
      icon: <Recycle className="h-8 w-8 text-primary" />,
      title: t.rechargeTitle,
      description: t.rechargeDescription,
    },
    {
      icon: <Droplets className="h-8 w-8 text-primary" />,
      title: t.conserveTitle,
      description: t.conserveDescription,
    },
    {
      icon: <ShieldCheck className="h-8 w-8 text-primary" />,
      title: t.qualityTitle,
      description: t.qualityDescription,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Card - Moved Up */}
      <Card className="w-full text-center p-8 shadow-lg">
        <CardHeader>
          <CardTitle className="text-4xl font-bold">{t.welcome}</CardTitle>
          <CardDescription className="text-lg text-muted-foreground mt-2">
            {t.welcomeDescription}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button size="lg" onClick={() => onNavigate('chat')}>
            {t.askTheAI}
          </Button>
        </CardContent>
      </Card>

      {/* Educational Content Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {infoCards.map((card, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Card className="h-full">
              <CardHeader className="items-center text-center">
                <div className="p-3 bg-muted rounded-full mb-4">
                  {card.icon}
                </div>
                <CardTitle>{card.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground text-center">
                  {card.description}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default HomePage;