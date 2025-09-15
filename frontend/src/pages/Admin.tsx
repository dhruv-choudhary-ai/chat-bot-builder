import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/layout/Navbar";
import { BotCard } from "@/components/bot/BotCard";
import { CreateBotModal } from "@/components/bot/CreateBotModal";
import { Plus } from "lucide-react";

interface Bot {
  id: string;
  name: string;
  type: string;
  status: "active" | "inactive";
  createdAt: string;
}

const Admin = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleCreateBot = (name: string, type: string) => {
    const newBot: Bot = {
      id: Date.now().toString(),
      name,
      type,
      status: "active",
      createdAt: new Date().toLocaleDateString()
    };
    setBots([...bots, newBot]);
    setIsCreateModalOpen(false);
  };

  const handleDeleteBot = (id: string) => {
    setBots(bots.filter(bot => bot.id !== id));
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-60 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Good Morning, Dhruv</h1>
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
                  bot={bot} 
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
      />
    </div>
  );
};

export default Admin;