import { useState, useEffect } from "react";
import { Users, Mail, Phone, Clock, MessageSquare, UserCheck, Search } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { conversationsAPI } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface User {
  id: number;
  email: string;
  name?: string;
  phone_number?: string;
  conversationCount: number;
  lastConversation: string;
  status: 'active' | 'inactive';
  channels: string[];
  firstInteraction: string;
}

interface UsersComponentProps {
  botId?: string;
}

export const UsersComponent = ({ botId }: UsersComponentProps) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (!botId) return;

    const fetchUsers = async () => {
      try {
        setLoading(true);
        console.log("👥 FETCHING USERS FOR BOT ID:", botId);
        console.log("📡 Users API Endpoint:", `/admin/bots/${botId}/conversations`);
        
        // Get all conversations for this bot
        const conversations = await conversationsAPI.getBotAllConversations(parseInt(botId));
        console.log("📊 Bot", botId, "user conversations received:", conversations.length);
        
        if (conversations.length === 0) {
          setUsers([]);
          return;
        }

        // Group conversations by user and build user profiles
        const userMap = new Map<number, User>();
        
        for (const conv of conversations) {
          const userId = conv.user_id;
          
          if (!userMap.has(userId)) {
            // Fetch user details
            try {
              const userDetails = await conversationsAPI.getBotUserDetails(parseInt(botId), userId);
              userMap.set(userId, {
                id: userId,
                email: userDetails.email,
                name: userDetails.name,
                phone_number: userDetails.phone_number,
                conversationCount: 0,
                lastConversation: '',
                status: 'active',
                channels: [],
                firstInteraction: conv.created_at
              });
            } catch (error) {
              console.error(`Failed to fetch user ${userId} details:`, error);
              // Create user with minimal info
              userMap.set(userId, {
                id: userId,
                email: `user${userId}@example.com`,
                name: `User ${userId}`,
                phone_number: undefined,
                conversationCount: 0,
                lastConversation: '',
                status: 'active',
                channels: [],
                firstInteraction: conv.created_at
              });
            }
          }
          
          const user = userMap.get(userId)!;
          user.conversationCount++;
          
          // Update last conversation time
          if (new Date(conv.created_at) > new Date(user.lastConversation || '1970-01-01')) {
            user.lastConversation = conv.created_at;
          }
          
          // Update first interaction time  
          if (new Date(conv.created_at) < new Date(user.firstInteraction)) {
            user.firstInteraction = conv.created_at;
          }
          
          // Add channel if not already present
          const channel = conv.interaction.channel || 'web';
          if (!user.channels.includes(channel)) {
            user.channels.push(channel);
          }
        }
        
        // Convert to array and sort by last conversation
        const usersArray = Array.from(userMap.values()).sort(
          (a, b) => new Date(b.lastConversation).getTime() - new Date(a.lastConversation).getTime()
        );
        
        console.log("✅ Bot", botId, "processed users:", usersArray.length);
        console.log("👤 User list for bot", botId, ":", usersArray.map(u => `${u.name || u.email} (${u.conversationCount} convs)`));
        setUsers(usersArray);
        
      } catch (error) {
        console.error('Failed to fetch users:', error);
        toast({
          title: "Error",
          description: "Failed to load users",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [botId, toast]);

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getChannelBadgeColor = (channel: string) => {
    switch (channel) {
      case 'whatsapp':
        return 'bg-green-100 text-green-800';
      case 'email':
        return 'bg-purple-100 text-purple-800';
      case 'sms':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!botId) {
    return (
      <div className="text-gray-400 text-center py-12">
        <div className="mb-4">
          <Users className="h-12 w-12 mx-auto text-gray-500" />
        </div>
        <p>Bot ID not provided</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Users List */}
        <div className="lg:w-1/2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Users ({filteredUsers.length})
              </CardTitle>
              <div className="flex gap-2">
                <Input
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="flex-1"
                />
                <Button variant="outline" size="icon">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-600">Loading users...</p>
                </div>
              ) : filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <div
                    key={user.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedUser?.id === user.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedUser(user)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900">
                            {user.name || user.email.split('@')[0]}
                          </h3>
                          <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                            {user.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{user.email}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <MessageSquare className="h-3 w-3" />
                            {user.conversationCount} conversations
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(user.lastConversation).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {user.channels.map((channel) => (
                        <Badge 
                          key={channel} 
                          variant="outline" 
                          className={`text-xs ${getChannelBadgeColor(channel)}`}
                        >
                          {channel}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p className="text-gray-600">No users found</p>
                  <p className="text-sm text-gray-500">Users will appear here after they interact with your bot</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* User Details */}
        <div className="lg:w-1/2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5" />
                User Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedUser ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      {selectedUser.name || selectedUser.email.split('@')[0]}
                    </h3>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 text-gray-500" />
                        <span className="text-sm">{selectedUser.email}</span>
                      </div>
                      {selectedUser.phone_number && (
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{selectedUser.phone_number}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm font-medium text-gray-700">Conversations</p>
                      <p className="text-2xl font-bold text-gray-900">{selectedUser.conversationCount}</p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm font-medium text-gray-700">Status</p>
                      <Badge variant={selectedUser.status === 'active' ? 'default' : 'secondary'} className="mt-1">
                        {selectedUser.status}
                      </Badge>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Channels Used</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedUser.channels.map((channel) => (
                        <Badge 
                          key={channel}
                          variant="outline"
                          className={getChannelBadgeColor(channel)}
                        >
                          {channel}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div>
                      <p className="text-sm font-medium text-gray-700">First Interaction</p>
                      <p className="text-sm text-gray-600">
                        {new Date(selectedUser.firstInteraction).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Last Conversation</p>
                      <p className="text-sm text-gray-600">
                        {new Date(selectedUser.lastConversation).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <UserCheck className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p className="text-gray-600">Select a user to view details</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
