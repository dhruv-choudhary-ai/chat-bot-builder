import { useState } from "react";
import { 
  Megaphone, 
  Plus, 
  Search, 
  Image as ImageIcon, 
  Send, 
  Check, 
  Clock, 
  Edit,
  Sparkles,
  MessageCircle,
  Mail,
  Instagram
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface Channel {
  id: string;
  name: string;
  icon: React.ReactNode;
  sent: boolean;
  sentAt?: string;
  reach?: number;
}

interface Campaign {
  id: string;
  title: string;
  description: string;
  image?: string;
  createdAt: string;
  status: 'draft' | 'generating' | 'ready' | 'sending' | 'sent';
  channels: Channel[];
  totalReach: number;
}

export const Marketing = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    title: '',
    description: '',
    image: null as File | null
  });

  const channels: Channel[] = [
    { id: 'whatsapp', name: 'WhatsApp', icon: <MessageCircle className="h-4 w-4 text-green-500" />, sent: false },
    { id: 'telegram', name: 'Telegram', icon: <Send className="h-4 w-4 text-blue-500" />, sent: false },
    { id: 'email', name: 'Email', icon: <Mail className="h-4 w-4 text-red-500" />, sent: false },
    { id: 'messenger', name: 'Messenger', icon: <MessageCircle className="h-4 w-4 text-blue-600" />, sent: false },
    { id: 'instagram', name: 'Instagram', icon: <Instagram className="h-4 w-4 text-pink-500" />, sent: false },
  ];

  const campaigns: Campaign[] = [
    {
      id: 'camp-1',
      title: 'Summer Sale 2025',
      description: 'Promote 30% off summer collection with beach vibes',
      image: '/placeholder.svg',
      createdAt: '2025-09-01',
      status: 'sent',
      totalReach: 45000,
      channels: [
        { id: 'whatsapp', name: 'WhatsApp', icon: <MessageCircle className="h-4 w-4 text-green-500" />, sent: true, sentAt: '2025-09-01 10:00', reach: 12000 },
        { id: 'telegram', name: 'Telegram', icon: <Send className="h-4 w-4 text-blue-500" />, sent: true, sentAt: '2025-09-01 10:05', reach: 8000 },
        { id: 'email', name: 'Email', icon: <Mail className="h-4 w-4 text-red-500" />, sent: true, sentAt: '2025-09-01 10:10', reach: 15000 },
        { id: 'messenger', name: 'Messenger', icon: <MessageCircle className="h-4 w-4 text-blue-600" />, sent: false },
        { id: 'instagram', name: 'Instagram', icon: <Instagram className="h-4 w-4 text-pink-500" />, sent: true, sentAt: '2025-09-01 10:15', reach: 10000 },
      ]
    },
    {
      id: 'camp-2',
      title: 'New Product Launch',
      description: 'Announce revolutionary AI-powered smartwatch',
      image: '/placeholder.svg',
      createdAt: '2025-09-05',
      status: 'ready',
      totalReach: 0,
      channels: [
        { id: 'whatsapp', name: 'WhatsApp', icon: <MessageCircle className="h-4 w-4 text-green-500" />, sent: false },
        { id: 'telegram', name: 'Telegram', icon: <Send className="h-4 w-4 text-blue-500" />, sent: false },
        { id: 'email', name: 'Email', icon: <Mail className="h-4 w-4 text-red-500" />, sent: false },
        { id: 'messenger', name: 'Messenger', icon: <MessageCircle className="h-4 w-4 text-blue-600" />, sent: false },
        { id: 'instagram', name: 'Instagram', icon: <Instagram className="h-4 w-4 text-pink-500" />, sent: false },
      ]
    },
    {
      id: 'camp-3',
      title: 'Black Friday Preview',
      description: 'Early access deals for VIP customers',
      createdAt: '2025-09-07',
      status: 'generating',
      totalReach: 0,
      channels: channels
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'text-gray-400 bg-gray-400/10';
      case 'generating': return 'text-yellow-400 bg-yellow-400/10';
      case 'ready': return 'text-blue-400 bg-blue-400/10';
      case 'sending': return 'text-orange-400 bg-orange-400/10';
      case 'sent': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft': return <Edit className="h-3 w-3" />;
      case 'generating': return <Sparkles className="h-3 w-3" />;
      case 'ready': return <Check className="h-3 w-3" />;
      case 'sending': return <Send className="h-3 w-3" />;
      case 'sent': return <Check className="h-3 w-3" />;
      default: return <Clock className="h-3 w-3" />;
    }
  };

  const filteredCampaigns = campaigns.filter(campaign =>
    campaign.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedCamp = campaigns.find(c => c.id === selectedCampaign);

  const handleCreateCampaign = () => {
    if (!newCampaign.title.trim() || !newCampaign.description.trim()) return;
    
    // Here you would typically send to backend AI for content generation
    console.log('Creating campaign:', newCampaign);
    
    setNewCampaign({ title: '', description: '', image: null });
    setShowCreateModal(false);
  };

  const handleSendToChannel = (campaignId: string, channelId: string) => {
    // Here you would send to the specific channel
    console.log(`Sending campaign ${campaignId} to ${channelId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Marketing Campaigns</h1>
          <p className="text-gray-400">Create AI-powered content for all your channels</p>
        </div>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Campaign
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{campaigns.length}</p>
              <p className="text-gray-400 text-sm">Total Campaigns</p>
            </div>
          </CardContent>
        </Card>
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400">
                {campaigns.filter(c => c.status === 'sent').length}
              </p>
              <p className="text-gray-400 text-sm">Campaigns Sent</p>
            </div>
          </CardContent>
        </Card>
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-400">
                {campaigns.reduce((acc, c) => acc + c.totalReach, 0).toLocaleString()}
              </p>
              <p className="text-gray-400 text-sm">Total Reach</p>
            </div>
          </CardContent>
        </Card>
        <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-400">5</p>
              <p className="text-gray-400 text-sm">Active Channels</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Campaigns List */}
        <div className="col-span-7">
          <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center space-x-2">
                  <Megaphone className="h-5 w-5" />
                  <span>Your Campaigns</span>
                </CardTitle>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search campaigns..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="space-y-1">
                {filteredCampaigns.map((campaign) => (
                  <div
                    key={campaign.id}
                    onClick={() => setSelectedCampaign(campaign.id)}
                    className={`p-4 border-b border-gray-600/30 hover:bg-gray-700/30 cursor-pointer transition-colors ${
                      selectedCampaign === campaign.id ? 'bg-gray-700/50' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      {campaign.image ? (
                        <img src={campaign.image} alt="" className="w-12 h-12 rounded-lg object-cover" />
                      ) : (
                        <div className="w-12 h-12 bg-gray-600 rounded-lg flex items-center justify-center">
                          <ImageIcon className="h-6 w-6 text-gray-400" />
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="text-white font-medium">{campaign.title}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(campaign.status)}`}>
                            {getStatusIcon(campaign.status)}
                            <span>{campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}</span>
                          </span>
                        </div>
                        <p className="text-gray-400 text-sm mt-1">{campaign.description}</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-gray-400 text-xs">{campaign.createdAt}</span>
                          {campaign.totalReach > 0 && (
                            <span className="text-gray-400 text-xs">
                              Reached: {campaign.totalReach.toLocaleString()}
                            </span>
                          )}
                          <div className="flex items-center space-x-1">
                            {campaign.channels.filter(c => c.sent).map(channel => (
                              <div key={channel.id} className="text-green-400">
                                {channel.icon}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Campaign Details */}
        <div className="col-span-5">
          <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
            <CardHeader>
              <CardTitle className="text-white text-sm">Campaign Details</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedCamp ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-white font-semibold mb-2">{selectedCamp.title}</h3>
                    <p className="text-gray-400 text-sm">{selectedCamp.description}</p>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-white font-medium">Channels</h4>
                    {selectedCamp.channels.map((channel) => (
                      <div key={channel.id} className="flex items-center justify-between p-3 bg-gray-800/30 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {channel.icon}
                          <div>
                            <p className="text-white text-sm font-medium">{channel.name}</p>
                            {channel.sent && channel.sentAt && (
                              <p className="text-gray-400 text-xs">Sent: {channel.sentAt}</p>
                            )}
                            {channel.reach && (
                              <p className="text-gray-400 text-xs">Reach: {channel.reach.toLocaleString()}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {channel.sent ? (
                            <div className="flex items-center space-x-1 text-green-400">
                              <Check className="h-4 w-4" />
                              <span className="text-xs">Sent</span>
                            </div>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleSendToChannel(selectedCamp.id, channel.id)}
                              disabled={selectedCamp.status !== 'ready'}
                              className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1"
                            >
                              <Send className="h-3 w-3 mr-1" />
                              Send
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {selectedCamp.status === 'ready' && (
                    <div className="pt-4 border-t border-gray-600/30">
                      <Button className="w-full bg-green-600 hover:bg-green-700 text-white">
                        <Send className="h-4 w-4 mr-2" />
                        Send to All Channels
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Megaphone className="h-12 w-12 mx-auto text-gray-500 mb-4" />
                  <p className="text-gray-400">Select a campaign to view details</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Sparkles className="h-5 w-5 text-yellow-400" />
                <span>Create AI Campaign</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm">Campaign Title</label>
                <Input
                  value={newCampaign.title}
                  onChange={(e) => setNewCampaign({...newCampaign, title: e.target.value})}
                  placeholder="e.g., Summer Sale 2025"
                  className="mt-1 bg-gray-800/50 border-gray-600 text-white"
                />
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">What's this campaign about?</label>
                <Textarea
                  value={newCampaign.description}
                  onChange={(e) => setNewCampaign({...newCampaign, description: e.target.value})}
                  placeholder="Describe your campaign... AI will create optimized content for each platform"
                  className="mt-1 bg-gray-800/50 border-gray-600 text-white h-24"
                />
              </div>

              <div>
                <label className="text-gray-400 text-sm">Supporting Image (Optional)</label>
                <div className="mt-1 border-2 border-dashed border-gray-600 rounded-lg p-6 text-center">
                  <ImageIcon className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                  <p className="text-gray-400 text-sm">Upload an image to enhance your campaign</p>
                  <input type="file" accept="image/*" className="hidden" />
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <Button
                  onClick={() => setShowCreateModal(false)}
                  variant="outline"
                  className="flex-1 border-gray-600 text-gray-400 hover:text-white"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateCampaign}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Content
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
