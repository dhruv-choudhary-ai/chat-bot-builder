import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageCircle, Send, X, Minimize2, Maximize2 } from "lucide-react";

interface ChatbotPreviewProps {
  botName: string;
  botType: string;
  primaryColor?: string;
  position?: "bottom-right" | "bottom-left";
}

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

export const ChatbotPreview = ({ 
  botName, 
  botType, 
  primaryColor = "#3B82F6",
  position = "bottom-right"
}: ChatbotPreviewProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: `Hi! I'm ${botName}, your ${botType.toLowerCase()} assistant. How can I help you today?`,
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState("");

  const sampleResponses = [
    "Thanks for your message! I'm here to help you with any questions you might have.",
    "That's a great question! Let me provide you with some information about that.",
    "I understand what you're looking for. Here are some options I can suggest:",
    "I'm glad you asked! This is definitely something I can assist you with.",
    "Let me help you find the best solution for your needs."
  ];

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");

    // Simulate bot response after a delay
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: sampleResponses[Math.floor(Math.random() * sampleResponses.length)],
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const positionClasses = position === "bottom-right" 
    ? "bottom-4 right-4" 
    : "bottom-4 left-4";

  return (
    <div className={`fixed ${positionClasses} z-50`}>
      {!isOpen ? (
        // Chat Button
        <Button
          onClick={() => setIsOpen(true)}
          className="rounded-full w-14 h-14 shadow-lg hover:scale-105 transition-transform"
          style={{ backgroundColor: primaryColor }}
        >
          <MessageCircle className="h-6 w-6 text-white" />
        </Button>
      ) : (
        // Chat Window
        <Card 
          className={`w-80 shadow-xl border-none transition-all duration-300 ${
            isMinimized ? 'h-12' : 'h-96'
          }`}
          style={{ backgroundColor: 'hsl(230, 5%, 15%)' }}
        >
          {/* Header */}
          <div 
            className="flex items-center justify-between p-3 rounded-t-lg cursor-pointer"
            style={{ backgroundColor: primaryColor }}
            onClick={() => setIsMinimized(!isMinimized)}
          >
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <MessageCircle className="h-4 w-4 text-white" />
              </div>
              <div>
                <h4 className="text-white font-medium text-sm">{botName}</h4>
                <p className="text-white/80 text-xs">Online</p>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-white hover:bg-white/10"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsMinimized(!isMinimized);
                }}
              >
                {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-white hover:bg-white/10"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsOpen(false);
                }}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages */}
              <CardContent className="p-0">
                <div className="h-64 overflow-y-auto p-3 space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-2 text-sm ${
                          message.isBot
                            ? 'bg-gray-700 text-white'
                            : 'text-white'
                        }`}
                        style={message.isBot ? {} : { backgroundColor: primaryColor }}
                      >
                        {message.text}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>

              {/* Input */}
              <div className="p-3 border-t border-gray-700">
                <div className="flex space-x-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    className="flex-1 bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                  />
                  <Button
                    onClick={handleSendMessage}
                    size="sm"
                    className="text-white"
                    style={{ backgroundColor: primaryColor }}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </Card>
      )}
    </div>
  );
};
