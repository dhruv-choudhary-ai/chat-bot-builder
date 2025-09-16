import { useState, useRef, useEffect } from "react";
import { MessageSquare, User, Clock, Search, MoreVertical, Send } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { conversationsAPI } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

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
  userEmail: string;
  lastMessage: string;
  lastMessageTime: string;
  messageCount: number;
  status: 'open' | 'resolved';
  messages: Message[];
  channel: string;
}

interface ConversationsProps {
  botId?: string;
}

export const Conversations = ({ botId }: ConversationsProps) => {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [replyText, setReplyText] = useState('');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Fetch conversations when botId changes
  useEffect(() => {
    if (!botId) return;

    const fetchConversations = async () => {
      try {
        console.log("🤖 FETCHING CONVERSATIONS FOR BOT ID:", botId);
        console.log("📡 API Endpoint:", `/admin/bots/${botId}/conversations`);
        
        // Use the simpler endpoint to get all conversations for this bot
        const allConversations = await conversationsAPI.getBotAllConversations(parseInt(botId));
        console.log("📊 Bot", botId, "conversations received:", allConversations.length);
        console.log("📋 Raw conversations data:", allConversations);
        
        if (allConversations.length === 0) {
          console.log("❌ No conversations found for bot", botId);
          setConversations([]);
          return;
        }

        // Group conversations by user
        const conversationsByUser = new Map<number, any>();
        
        for (const conv of allConversations) {
          const userId = conv.user_id;
          
          if (!conversationsByUser.has(userId)) {
            // Get user details
            try {
              const user = await conversationsAPI.getBotUserDetails(parseInt(botId), userId);
              conversationsByUser.set(userId, {
                id: `${userId}-conversations`,
                userId: userId.toString(),
                userName: user.name || user.email.split('@')[0],
                userEmail: user.email,
                lastMessage: '',
                lastMessageTime: '',
                messageCount: 0,
                status: 'open' as const,
                messages: [] as Message[],
                channel: conv.interaction.channel || 'web'
              });
            } catch (error) {
              console.error(`Failed to fetch user ${userId} details:`, error);
              // Use fallback user info
              conversationsByUser.set(userId, {
                id: `${userId}-conversations`,
                userId: userId.toString(),
                userName: `User ${userId}`,
                userEmail: `user${userId}@example.com`,
                lastMessage: '',
                lastMessageTime: '',
                messageCount: 0,
                status: 'open' as const,
                messages: [] as Message[],
                channel: conv.interaction.channel || 'web'
              });
            }
          }
          
          const userConv = conversationsByUser.get(userId)!;
          const timestamp = new Date(conv.created_at).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          });
          
          // Add user question
          if (conv.interaction.question) {
            userConv.messages.push({
              id: `${conv.id}-q`,
              content: conv.interaction.question,
              sender: 'user',
              timestamp: timestamp
            });
          }
          
          // Add bot answer
          if (conv.interaction.answer) {
            userConv.messages.push({
              id: `${conv.id}-a`,
              content: conv.interaction.answer,
              sender: 'bot',
              timestamp: timestamp
            });
          }
          
          // Update last message and time
          if (conv.interaction.answer) {
            userConv.lastMessage = conv.interaction.answer;
            userConv.lastMessageTime = new Date(conv.created_at).toLocaleString();
          } else if (conv.interaction.question && !userConv.lastMessage) {
            userConv.lastMessage = conv.interaction.question;
            userConv.lastMessageTime = new Date(conv.created_at).toLocaleString();
          }
          
          userConv.messageCount = userConv.messages.length;
          userConv.status = conv.resolved ? 'resolved' : 'open';
        }
        
        const processedConversations = Array.from(conversationsByUser.values());
        console.log("✅ Bot", botId, "processed conversations:", processedConversations.length);
        console.log("👥 Users found for bot", botId, ":", processedConversations.map(c => `${c.userName} (${c.userEmail})`));
        console.log("📈 Conversation summary for bot", botId, ":", processedConversations.map(c => `${c.userName}: ${c.messageCount} messages`));
        
        setConversations(processedConversations);
        
        // Auto-select first conversation if none selected
        if (processedConversations.length > 0 && !selectedConversation) {
          setSelectedConversation(processedConversations[0].id);
        }
        
      } catch (error) {
        console.error('Failed to fetch conversations:', error);
        toast({
          title: "Error",
          description: "Failed to load conversations",
          variant: "destructive",
        });
      }
    };

    fetchConversations();
  }, [botId, toast]);

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

  const filteredConversations = conversations.filter(conv =>
    conv.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.lastMessage.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedConv = conversations.find(conv => conv.id === selectedConversation);
  const selectedUser = selectedConv ? {
    id: selectedConv.userId,
    name: selectedConv.userName,
    email: selectedConv.userEmail,
    phone: '',
    location: '',
    joinDate: '',
    totalConversations: 1,
    lastActive: selectedConv.lastMessageTime,
    status: selectedConv.status === 'open' ? 'online' : 'offline'
  } : null;

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
