import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import MessageBubble from '../MessageBubble';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Textarea';
import { ScrollArea } from '../ui/ScrollArea';
import { saveMessage, getMessages } from '../../utils/firebase'; // Import firebase functions

const roleSpecificPrompts = {
    'General User': ["What is the groundwater status in my district?", "Explain the meaning of Safe / Semi-Critical / Critical.", "Show me water usage trends for my state.", "Give me tips to save water at home."],
    'Researcher': ["Give me historical groundwater extraction trends for 2010–2020.", "Provide recharge vs extraction graphs for Punjab.", "Download aquifer-level datasets in CSV.", "Compare seasonal fluctuations in recharge across states."],
    'Planner': ["Show projected demand vs supply for 2030.", "List critical blocks in my state with over-extraction.", "Generate planning map with red-flagged zones.", "Give me intervention strategies for semi-critical areas."],
    'Farmer': ["What is the best crop for my area?", "How to check the water level in my well?", "Show me tips for efficient irrigation.", "What government subsidies are available for farmers?"],
};

const getMockBotResponse = (message, language) => {
    if (language === 'hi') {
        return `यह आपके संदेश के लिए एक हिंदी प्रतिक्रिया है: "${message}"`;
    }
    return `This is an English response for your message: "${message}"`;
};

const ChatPage = ({ user, language }) => {
    const [messages, setMessages] = useState([]); // Start with an empty array
    const [input, setInput] = useState('');
    const scrollAreaRef = useRef();
    const suggestions = roleSpecificPrompts[user.role] || roleSpecificPrompts['General User'];

    // Fetch messages when the component loads
    useEffect(() => {
        if (user && user.uid) {
            const unsubscribe = getMessages(user.uid, (loadedMessages) => {
                if (loadedMessages.length === 0) {
                    setMessages([{ id: 1, content: language === 'hi' ? `नमस्ते! मैं नीरनीति एआई सहायक हूँ। मैं आपकी कैसे मदद कर सकता हूँ?` : `Hello! I'm the NeerNiti AI assistant. How can I help you today?`, isBot: true }]);
                } else {
                    setMessages(loadedMessages);
                }
            });
            return () => unsubscribe(); // Cleanup subscription on unmount
        }
    }, [user, language]);

    const handleSend = async () => { // Make function async
        if (input.trim() === '' || !user) return;
        
        const userMessage = { content: input, isBot: false };
        await saveMessage(user.uid, userMessage);
        
        const botResponseContent = getMockBotResponse(input, language);
        const botMessage = { content: botResponseContent, isBot: true };
        
        setTimeout(async () => {
            await saveMessage(user.uid, botMessage);
        }, 1000);

        setInput('');
    };

    useEffect(() => {
        if (scrollAreaRef.current?.viewport) {
            scrollAreaRef.current.viewport.scrollTop = scrollAreaRef.current.viewport.scrollHeight;
        }
    }, [messages]);

    return (
        <div className="flex flex-col h-[calc(100vh-120px)] bg-card rounded-lg border">
            <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
                <div className="space-y-6">
                    {messages.map((msg) => (
                        <MessageBubble key={msg.id} message={msg} isBot={msg.isBot} />
                    ))}
                </div>
            </ScrollArea>
            <div className="p-4 border-t">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
                    {suggestions.map((prompt, index) => (
                        <Button key={index} variant="outline" size="sm" className="h-auto text-wrap text-left" onClick={() => setInput(prompt)}>
                            {prompt}
                        </Button>
                    ))}
                </div>
                <div className="relative">
                    <Textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())} placeholder={language === 'hi' ? 'कुछ भी पूछें...' : 'Ask anything...'} className="pr-16 resize-none min-h-[52px]" />
                    <Button onClick={handleSend} size="icon" className="absolute right-3 top-1/2 -translate-y-1/2 h-9 w-9">
                        <Send className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;