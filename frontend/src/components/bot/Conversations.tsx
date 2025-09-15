import { useState, useRef, useEffect } from "react";
import { MessageSquare, User, Clock, Search, MoreVertical, Send } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot' | 'admin';
  timestamp: string;
}

interface Conversation {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  lastMessage: string;
  lastMessageTime: string;
  messageCount: number;
  status: 'open' | 'resolved';
  messages: Message[];
}

interface UserDetails {
  id: string;
  name: string;
  email: string;
  phone?: string;
  location?: string;
  joinDate: string;
  totalConversations: number;
  lastActive: string;
  status: 'online' | 'offline' | 'away';
}

export const Conversations = () => {
  const [selectedConversation, setSelectedConversation] = useState<string | null>('conv-1');
  const [searchTerm, setSearchTerm] = useState('');
  const [replyText, setReplyText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: 'conv-1',
      userId: 'user-1',
      userName: 'John Smith',
      lastMessage: 'Thanks for the help with my order!',
      lastMessageTime: '2 min ago',
      messageCount: 12,
      status: 'open',
      messages: [
        { id: 'msg-1', content: 'Hi, I need help with my recent order', sender: 'user', timestamp: '10:30 AM' },
        { id: 'msg-2', content: 'Hello! I\'d be happy to help you with your order. Can you provide your order number?', sender: 'bot', timestamp: '10:31 AM' },
        { id: 'msg-3', content: 'Sure, it\'s #ORD-12345', sender: 'user', timestamp: '10:32 AM' },
        { id: 'msg-4', content: 'I found your order. It\'s currently being processed and will ship within 2 business days.', sender: 'bot', timestamp: '10:33 AM' },
        { id: 'msg-5', content: 'Thanks for the help with my order!', sender: 'user', timestamp: '10:35 AM' },
      ]
    },
    {
      id: 'conv-2',
      userId: 'user-2',
      userName: 'Sarah Johnson',
      lastMessage: 'Can you help me reset my password?',
      lastMessageTime: '15 min ago',
      messageCount: 8,
      status: 'open',
      messages: [
        { id: 'msg-6', content: 'I forgot my password and can\'t log in', sender: 'user', timestamp: '10:15 AM' },
        { id: 'msg-7', content: 'I can help you reset your password. Please provide your email address.', sender: 'bot', timestamp: '10:16 AM' },
        { id: 'msg-8', content: 'sarah.johnson@email.com', sender: 'user', timestamp: '10:17 AM' },
        { id: 'msg-9', content: 'Can you help me reset my password?', sender: 'user', timestamp: '10:20 AM' },
      ]
    },
    {
      id: 'conv-3',
      userId: 'user-3',
      userName: 'Mike Davis',
      lastMessage: 'Perfect, that solved my issue!',
      lastMessageTime: '1 hour ago',
      messageCount: 6,
      status: 'resolved',
      messages: [
        { id: 'msg-10', content: 'Having trouble with the mobile app', sender: 'user', timestamp: '9:30 AM' },
        { id: 'msg-11', content: 'I can help with that. What specific issue are you experiencing?', sender: 'bot', timestamp: '9:31 AM' },
        { id: 'msg-12', content: 'Perfect, that solved my issue!', sender: 'user', timestamp: '9:35 AM' },
      ]
    }
  ]);

  const handleSendReply = () => {
    if (!replyText.trim() || !selectedConversation) return;
    
    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      content: replyText,
      sender: 'admin',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setConversations(prev => 
      prev.map(conv => 
        conv.id === selectedConversation 
          ? { 
              ...conv, 
              messages: [...conv.messages, newMessage],
              lastMessage: replyText,
              lastMessageTime: 'now'
            }
          : conv
      )
    );
    
    setReplyText('');
    
    // Scroll to bottom after sending message
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendReply();
    }
  };

  // Auto-scroll when conversation changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedConversation]);

  const userDetails: { [key: string]: UserDetails } = {
    'user-1': {
      id: 'user-1',
      name: 'John Smith',
      email: 'john.smith@email.com',
      phone: '+1 (555) 123-4567',
      location: 'New York, NY',
      joinDate: 'Jan 15, 2024',
      totalConversations: 8,
      lastActive: '2 min ago',
      status: 'online'
    },
    'user-2': {
      id: 'user-2',
      name: 'Sarah Johnson',
      email: 'sarah.johnson@email.com',
      phone: '+1 (555) 234-5678',
      location: 'Los Angeles, CA',
      joinDate: 'Mar 22, 2024',
      totalConversations: 12,
      lastActive: '15 min ago',
      status: 'away'
    },
    'user-3': {
      id: 'user-3',
      name: 'Mike Davis',
      email: 'mike.davis@email.com',
      location: 'Chicago, IL',
      joinDate: 'Feb 10, 2024',
      totalConversations: 5,
      lastActive: '1 hour ago',
      status: 'offline'
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.lastMessage.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedConv = conversations.find(conv => conv.id === selectedConversation);
  const selectedUser = selectedConv ? userDetails[selectedConv.userId] : null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-green-400';
      case 'resolved': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getUserStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'away': return 'bg-yellow-500';
      case 'offline': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="grid grid-cols-12 gap-4 h-full">
      {/* Section 1: Conversations List */}
      <div className="col-span-4">
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none h-full">
          <CardHeader className="pb-4">
            <CardTitle className="text-white text-lg font-semibold flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>Conversations</span>
            </CardTitle>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 focus:border-gray-500"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {filteredConversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setSelectedConversation(conv.id)}
                  className={`p-4 cursor-pointer border-b border-gray-600/30 hover:bg-gray-700/30 transition-colors ${
                    selectedConversation === conv.id ? 'bg-gray-700/50' : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-gray-300" />
                      </div>
                      <div>
                        <h4 className="text-white font-medium text-sm">{conv.userName}</h4>
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs font-medium ${getStatusColor(conv.status)}`}>
                            {conv.status.charAt(0).toUpperCase() + conv.status.slice(1)}
                          </span>
                          <span className="text-gray-400 text-xs">•</span>
                          <span className="text-gray-400 text-xs">{conv.messageCount} messages</span>
                        </div>
                      </div>
                    </div>
                    <span className="text-gray-400 text-xs">{conv.lastMessageTime}</span>
                  </div>
                  <p className="text-gray-400 text-sm truncate">{conv.lastMessage}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Section 2: Selected Conversation */}
      <div className="col-span-5">
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none h-full">
          <CardHeader className="pb-4">
            <CardTitle className="text-white text-lg font-semibold flex items-center justify-between">
              {selectedConv ? (
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-gray-300" />
                  </div>
                  <span>{selectedConv.userName}</span>
                </div>
              ) : (
                <span>Select a conversation</span>
              )}
              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex flex-col flex-1">
            {selectedConv ? (
              <>
                {/* Messages Area */}
                <div 
                  className="flex-1 space-y-4 max-h-80 overflow-y-auto p-4"
                  style={{
                    scrollbarWidth: 'thin',
                    scrollbarColor: '#4a5568 hsl(230, 5%, 15%)'
                  }}
                >
                  <style dangerouslySetInnerHTML={{
                    __html: `
                      .flex-1::-webkit-scrollbar {
                        width: 8px;
                      }
                      .flex-1::-webkit-scrollbar-track {
                        background: hsl(230, 5%, 15%);
                        border-radius: 4px;
                      }
                      .flex-1::-webkit-scrollbar-thumb {
                        background: #4a5568;
                        border-radius: 4px;
                        border: 1px solid hsl(230, 5%, 15%);
                      }
                      .flex-1::-webkit-scrollbar-thumb:hover {
                        background: #0a436e;
                      }
                      .flex-1::-webkit-scrollbar-corner {
                        background: hsl(230, 5%, 15%);
                      }
                      .space-y-1::-webkit-scrollbar {
                        width: 8px;
                      }
                      .space-y-1::-webkit-scrollbar-track {
                        background: hsl(230, 5%, 15%);
                        border-radius: 4px;
                      }
                      .space-y-1::-webkit-scrollbar-thumb {
                        background: #4a5568;
                        border-radius: 4px;
                        border: 1px solid hsl(230, 5%, 15%);
                      }
                      .space-y-1::-webkit-scrollbar-thumb:hover {
                        background: #0a436e;
                      }
                      .space-y-1::-webkit-scrollbar-corner {
                        background: hsl(230, 5%, 15%);
                      }
                    `
                  }} />
                  {selectedConv.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${(message.sender === 'bot' || message.sender === 'admin') ? 'justify-end ml-8' : 'justify-start'}`}
                    >
                      <div className="flex flex-col">
                        {/* Label for bot/admin messages */}
                        {(message.sender === 'bot' || message.sender === 'admin') && (
                          <div className="text-right mb-1">
                            <span className={`text-xs px-2 py-1 ${
                              message.sender === 'admin' 
                                ? 'text-black' 
                                : 'text-white'
                            }`}>
                              {message.sender === 'admin' ? '' : 'Bot'}
                            </span>
                          </div>
                        )}
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.sender === 'bot'
                              ? 'text-white'
                              : message.sender === 'admin'
                              ? 'text-white'
                              : 'bg-gray-700 text-gray-100'
                          }`}
                          style={
                            message.sender === 'bot' 
                              ? { backgroundColor: '#0a436e' } 
                              : message.sender === 'admin'
                              ? { backgroundColor: '#144d37' }
                              : {}
                          }
                        >
                          <p className="text-sm">{message.content}</p>
                          <p className={`text-xs mt-1 ${
                            message.sender === 'bot' 
                              ? 'text-blue-100' 
                              : message.sender === 'admin'
                              ? 'text-green-100'
                              : 'text-gray-400'
                          }`}>
                            {message.timestamp}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Reply Input Area */}
                <div className="border-t border-gray-600/30 p-4">
                  <div className="flex space-x-2">
                    <Input
                      placeholder="Type your reply..."
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="flex-1 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 focus:border-gray-500"
                    />
                    <Button
                      onClick={handleSendReply}
                      disabled={!replyText.trim()}
                      size="sm"
                      className="px-3"
                      style={{ backgroundColor: '#680606ff' }}
                    >
                      <Send className="h-4 w-4 text-white" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-500" />
                  <p>Select a conversation to view messages</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Section 3: User Details */}
      <div className="col-span-3">
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none h-full">
          <CardHeader className="pb-4">
            <CardTitle className="text-white text-lg font-semibold flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>User Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedUser ? (
              <div className="space-y-4">
                {/* User Avatar and Name */}
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
                    <User className="h-8 w-8 text-gray-300" />
                  </div>
                  <h3 className="text-white font-semibold">{selectedUser.name}</h3>
                  <div className="flex items-center justify-center space-x-2 mt-1">
                    <div className={`w-2 h-2 rounded-full ${getUserStatusColor(selectedUser.status)}`}></div>
                    <span className="text-gray-400 text-sm capitalize">{selectedUser.status}</span>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="space-y-3">
                  <div>
                    <label className="text-gray-400 text-xs font-medium">Email</label>
                    <p className="text-white text-sm">{selectedUser.email}</p>
                  </div>
                  
                  {selectedUser.phone && (
                    <div>
                      <label className="text-gray-400 text-xs font-medium">Phone</label>
                      <p className="text-white text-sm">{selectedUser.phone}</p>
                    </div>
                  )}
                  
                  {selectedUser.location && (
                    <div>
                      <label className="text-gray-400 text-xs font-medium">Location</label>
                      <p className="text-white text-sm">{selectedUser.location}</p>
                    </div>
                  )}
                </div>

                {/* Activity Information */}
                <div className="border-t border-gray-600/30 pt-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400 text-sm">Join Date</span>
                      <span className="text-white text-sm">{selectedUser.joinDate}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400 text-sm">Total Conversations</span>
                      <span className="text-white text-sm">{selectedUser.totalConversations}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400 text-sm">Last Active</span>
                      <span className="text-white text-sm flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{selectedUser.lastActive}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <User className="h-12 w-12 mx-auto mb-4 text-gray-500" />
                  <p>Select a conversation to view user details</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
