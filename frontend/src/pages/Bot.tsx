import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { 
  BarChart3, 
  MessageSquare, 
  // Megaphone, 
  Users, 
  TrendingUp, 
  Wrench, 
  // BookOpen, 
  Settings,
  Menu,
  HelpCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/layout/Navbar";
import { Overview } from "@/components/bot/Overview";
import { Conversations } from "@/components/bot/Conversations";
// import { Marketing } from "@/components/bot/Marketing";
import { UsersComponent } from "@/components/bot/UsersComponent";
import { Analytics } from "@/components/bot/Analytics";
import { Builder } from "@/components/bot/Builder";
// import { Train } from "@/components/bot/Train";
import { Configure } from "@/components/bot/Configure";
import { Help } from "@/components/bot/Help";
import { BotManagement } from "@/components/bot/BotManagement";
import { DeployModal } from "@/components/bot/DeployModal";
import { tokenManager } from "@/lib/api";

const Bot = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  // Authentication check
  useEffect(() => {
    if (!tokenManager.isAuthenticated()) {
      navigate("/login");
    }
  }, [navigate]);

  // Bot ID validation
  useEffect(() => {
    if (!id) {
      navigate("/admin");
    }
  }, [id, navigate]);
  
  // Bot information state
  const [botInfo, setBotInfo] = useState<{
    id: number;
    name: string;
    bot_type: string;
    admin_id: number;
  } | null>(null);
  const [isLoadingBot, setIsLoadingBot] = useState(true);
  
  // Fetch bot information
  useEffect(() => {
    const fetchBotInfo = async () => {
      if (!id) return;
      
      try {
        setIsLoadingBot(true);
        // For now, we'll create a mock bot info since there's no specific bot endpoint
        // In a real implementation, you'd call an API like: botsAPI.getBot(id)
        setBotInfo({
          id: parseInt(id),
          name: `Bot ${id}`,
          bot_type: "Retail Bot", // This would come from the API
          admin_id: 1 // This would come from the API
        });
      } catch (error) {
        console.error("Failed to fetch bot info:", error);
        navigate("/admin");
      } finally {
        setIsLoadingBot(false);
      }
    };
    
    fetchBotInfo();
  }, [id, navigate]);
  
  // Bot functionalities state
  const [functionalities, setFunctionalities] = useState([
    { id: 'customer-support', name: 'Customer Support', enabled: true },
    { id: 'lead-generation', name: 'Lead Generation', enabled: true },
    { id: 'appointment-booking', name: 'Appointment Booking', enabled: false },
    { id: 'product-recommendations', name: 'Product Recommendations', enabled: true },
    { id: 'order-tracking', name: 'Order Tracking', enabled: false },
    { id: 'faq-assistance', name: 'FAQ Assistance', enabled: true },
    { id: 'feedback-collection', name: 'Feedback Collection', enabled: false },
    { id: 'multi-language', name: 'Multi-language Support', enabled: false },
  ]);
  
  // Functionalities confirmation state
  const [functionalitiesConfirmed, setFunctionalitiesConfirmed] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  
  // Training and deployment state
  const [botStatus, setBotStatus] = useState({
    trained: true,
    deployed: false
  });
  
  // Deploy modal state
  const [isDeployModalOpen, setIsDeployModalOpen] = useState(false);

  const toggleFunctionality = (id: string) => {
    if (!functionalitiesConfirmed || isEditing) {
      setFunctionalities(prev => 
        prev.map(func => 
          func.id === id ? { ...func, enabled: !func.enabled } : func
        )
      );
    }
  };

  const confirmFunctionalities = () => {
    setFunctionalitiesConfirmed(true);
    setIsEditing(false);
  };

  const editFunctionalities = () => {
    setIsEditing(true);
  };

  const handleTrainBot = () => {
    setBotStatus(prev => ({ ...prev, trained: true }));
  };

  const handleDeployBot = () => {
    if (botStatus.trained) {
      setIsDeployModalOpen(true);
    }
  };

  const navItems = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "conversations", label: "Conversations", icon: MessageSquare },
    // { id: "marketing", label: "Marketing Campaigns", icon: Megaphone },
    { id: "users", label: "Users", icon: Users },
    { id: "analytics", label: "Analytics", icon: TrendingUp },
    { id: "builder", label: "Builder", icon: Wrench },
    // { id: "train", label: "Train", icon: BookOpen },
    { id: "configure", label: "Configure", icon: Settings },
  ];

  const helpItem = { id: "help", label: "Help", icon: HelpCircle };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="flex" style={{ height: 'calc(100vh - 73px)' }}>
        {/* Left Sidebar */}
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} border-r border-border transition-all duration-300 flex flex-col`} style={{ backgroundColor: 'hsl(230, 5%, 15%)' }}>
          {/* Hamburger Menu Button */}
          <div className="px-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 w-full justify-start"
            >
              <Menu className="h-5 w-5" />
              {!sidebarCollapsed && <span className="ml-2">Menu</span>}
            </Button>
            {/* Separator Line */}
            <div className="border-b border-gray-600 my-2"></div>
          </div>

        {/* Navigation */}
        <div className="p-3 flex flex-col h-full">
          <nav className="space-y-2 flex-1">
            {navItems.map((item) => {
              const IconComponent = item.icon;
              const isActive = activeTab === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'space-x-3 px-3'} py-2 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-gray-700/50 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
                  }`}
                  title={sidebarCollapsed ? item.label : undefined}
                >
                  <IconComponent className="h-5 w-5" />
                  {!sidebarCollapsed && <span>{item.label}</span>}
                </button>
              );
            })}
          </nav>
          
          {/* Help Section at Bottom */}
          <div className="mt-auto pt-4 border-t border-border/20">
            <button
              onClick={() => setActiveTab(helpItem.id)}
              className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'space-x-3 px-3'} py-2 rounded-lg text-sm transition-colors ${
                activeTab === helpItem.id
                  ? 'bg-gray-700/50 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
              }`}
              title={sidebarCollapsed ? helpItem.label : undefined}
            >
              <HelpCircle className="h-5 w-5" />
              {!sidebarCollapsed && <span>{helpItem.label}</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-5 overflow-y-auto">
        {/* Loading State */}
        {isLoadingBot ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading bot information...</p>
            </div>
          </div>
        ) : botInfo ? (
          <div>
            
            {/* Main Content - Full Width */}
            <div>
          {activeTab === "overview" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Overview
                  functionalities={functionalities}
                  functionalitiesConfirmed={functionalitiesConfirmed}
                  isEditing={isEditing}
                  toggleFunctionality={toggleFunctionality}
                  confirmFunctionalities={confirmFunctionalities}
                  editFunctionalities={editFunctionalities}
                />
              </div>
              <div>
                <BotManagement
                  functionalities={functionalities}
                  functionalitiesConfirmed={functionalitiesConfirmed}
                  botStatus={botStatus}
                  handleTrainBot={handleTrainBot}
                  handleDeployBot={handleDeployBot}
                />
              </div>
            </div>
          )}
          {activeTab === "conversations" && <Conversations botId={id} />}
          {/* {activeTab === "marketing" && <Marketing />} */}
          {activeTab === "users" && <UsersComponent botId={id} />}
          {activeTab === "analytics" && <Analytics />}
          {activeTab === "builder" && <Builder botId={id} />}
          {activeTab === "configure" && <Configure />}
          {activeTab === "help" && <Help />}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <p className="text-muted-foreground">Bot not found</p>
            </div>
          </div>
        )}
      </div>
      </div>
      
      {/* Deploy Modal */}
      {botInfo && (
        <DeployModal 
          isOpen={isDeployModalOpen}
          onClose={() => setIsDeployModalOpen(false)}
          botInfo={botInfo}
        />
      )}
    </div>
  );
};

export default Bot;
