// src/components/MessageBubble.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { Card } from './ui/Card';
import { Avatar, AvatarFallback } from './ui/Avatar';
import { Bot, User } from 'lucide-react';

const MessageBubble = ({ message, isBot }) => {
  const alignment = isBot ? 'justify-start' : 'justify-end';
  const bubbleColor = isBot ? 'bg-card' : 'bg-primary text-primary-foreground';
  const roundedCorners = isBot ? 'rounded-tl-sm' : 'rounded-tr-sm';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 w-full ${alignment}`}
    >
      {isBot && (
        <Avatar className="h-8 w-8">
          <AvatarFallback className="bg-secondary"><Bot className="h-4 w-4" /></AvatarFallback>
        </Avatar>
      )}
      <div className="max-w-[75%]">
        <Card className={`p-3 rounded-lg ${bubbleColor} ${roundedCorners}`}>
          <p className="text-sm">{message.content}</p>
        </Card>
        <p className={`text-xs text-muted-foreground mt-1 px-1 ${isBot ? 'text-left' : 'text-right'}`}>
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
      {!isBot && (
        <Avatar className="h-8 w-8">
          <AvatarFallback><User className="h-4 w-4" /></AvatarFallback>
        </Avatar>
      )}
    </motion.div>
  );
};

export default MessageBubble;