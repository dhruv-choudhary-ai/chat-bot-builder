import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/layout/Navbar";
import { BotCard } from "@/components/bot/BotCard";
import { CreateBotModal } from "@/components/bot/CreateBotModal";
import { Plus } from "lucide-react";
import { botsAPI, authAPI, tokenManager, type Bot as APIBot, type AdminInfo } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

// Update interface to match backend
interface Bot {
  id: number;
  name: string;
  bot_type: string;
  admin_id: number;
  status?: "active" | "inactive";
  createdAt?: string;
}

const Admin = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [availableBotTypes, setAvailableBotTypes] = useState<string[]>([]);
  const [adminInfo, setAdminInfo] = useState<AdminInfo | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const loadData = async () => {
      try {
        // Check if user is authenticated
        if (!tokenManager.isAuthenticated()) {
          navigate("/login");
          return;
        }

        // Load admin info and bots in parallel
        const [adminData, botsData, botTypesData] = await Promise.all([
          authAPI.getCurrentAdmin(),
          botsAPI.getBots(),
          botsAPI.getAvailableBotTypes(),
        ]);

        setAdminInfo(adminData);
        setBots(botsData);
        setAvailableBotTypes(botTypesData);
      } catch (error) {
        console.error("Failed to load data:", error);
        toast({
          title: "Error",
          description: "Failed to load dashboard data. Please try logging in again.",
          variant: "destructive",
        });
        tokenManager.removeToken();
        navigate("/login");
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [navigate, toast]);

  const handleCreateBot = async (name: string, type: string) => {
    try {
      const newBot = await botsAPI.createBot(name, type);
      setBots([...bots, newBot]);
      setIsCreateModalOpen(false);
      toast({
        title: "Success",
        description: `Bot "${name}" created successfully!`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create bot",
        variant: "destructive",
      });
    }
  };

  const handleDeleteBot = async (id: string) => {
    // Note: Backend doesn't have delete endpoint, so we'll just remove from UI for now
    setBots(bots.filter(bot => bot.id.toString() !== id));
    toast({
      title: "Success",
      description: "Bot removed from dashboard",
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading your dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-60 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 18 ? 'Afternoon' : 'Evening'}, {adminInfo?.name || 'Admin'}
          </h1>
          {bots.length > 0 && (
            <p className="text-muted-foreground">{bots.length} bot{bots.length === 1 ? '' : 's'} deployed</p>
          )}
        </div>

        {bots.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="mb-8">
              <h2 className="text-4xl font-bold text-foreground mb-3">Welcome Aboard!</h2>
              <p className="text-xl text-muted-foreground mb-1">Let's make some bots</p>
              
              <div className="max-w-2xl mx-auto mb-1 text-center">
                <div className="space-y-1 text-sm text-muted-foreground">
                    <p>Build AI chatbots for customer support, lead generation, FAQ assistance, and more!</p>
                    <p>Train them with your data, customize responses, and monitor performance.</p>
                </div>
              </div>
            </div>
            
            <Button 
              onClick={() => setIsCreateModalOpen(true)}
              className="bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200 text-lg px-6 py-3 h-auto font-medium"
            >
              <Plus className="mr-2 h-5 w-5" />
              Create your first bot
            </Button>
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-foreground">Your Bots</h2>
              <Button 
                onClick={() => setIsCreateModalOpen(true)}
                className="bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200"
              >
                <Plus className="mr-2 h-4 w-4" />
                Create Bot
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {bots.map((bot) => (
                <BotCard 
                  key={bot.id} 
                  bot={{
                    id: bot.id.toString(),
                    name: bot.name,
                    type: bot.bot_type,
                    status: bot.status || "active",
                    createdAt: bot.createdAt || new Date().toLocaleDateString()
                  }} 
                  onDelete={handleDeleteBot}
                />
              ))}
            </div>
          </div>
        )}
      </main>

      <CreateBotModal 
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreateBot={handleCreateBot}
        availableBotTypes={availableBotTypes}
      />
    </div>
  );
};

export default Admin;