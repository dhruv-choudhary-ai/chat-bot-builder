import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Bot, MoreVertical, Briefcase, GraduationCap, ShoppingCart, Heart, MessageSquare, Calculator, BookOpen, Users, Globe, Zap } from "lucide-react";

interface Bot {
  id: string;
  name: string;
  type: string;
  status: "active" | "inactive";
  createdAt: string;
}

interface BotCardProps {
  bot: Bot;
  onDelete: (id: string) => void;
}

export const BotCard = ({ bot, onDelete }: BotCardProps) => {
  // Get bot type colors
  const getTypeColor = (type: string) => {
    const colors = {
      "Sales Bot": "bg-green-600",
      "Career Bot": "bg-blue-600", 
      "Retail Bot": "bg-purple-600",
      "Health Bot": "bg-orange-600",
      "Support Bot": "bg-cyan-600",
      "Finance Bot": "bg-indigo-600",
      "Learning Bot": "bg-pink-600",
      "HR Bot": "bg-teal-600",
      "Travel Bot": "bg-yellow-600",
      "Custom Bot": "bg-gray-600"
    };
    return colors[type as keyof typeof colors] || "bg-gray-600";
  };

  // Get bot type icon
  const getTypeIcon = (type: string) => {
    const icons = {
      "Sales Bot": Briefcase,
      "Career Bot": GraduationCap,
      "Retail Bot": ShoppingCart,
      "Health Bot": Heart,
      "Support Bot": MessageSquare,
      "Finance Bot": Calculator,
      "Learning Bot": BookOpen,
      "HR Bot": Users,
      "Travel Bot": Globe,
      "Custom Bot": Zap
    };
    return icons[type as keyof typeof icons] || Bot;
  };

  return (
    <Card className="group border-none hover:opacity-80 transition-all duration-200 relative" style={{ backgroundColor: 'hsl(230, 5%, 15%)' }}>
      {/* New Badge */}
      <div className="absolute top-3 left-3 z-10">
        <Badge className="bg-red-600 text-white text-xs px-2 py-1 rounded">
          New!
        </Badge>
      </div>

      {/* More Options */}
      <div className="absolute top-3 right-3 z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={(e) => {
            e.stopPropagation();
            e.preventDefault();
            if (window.confirm(`Are you sure you want to delete "${bot.name}"?`)) {
              onDelete(bot.id);
            }
          }}
          className="h-6 w-6 p-0 text-gray-400 hover:text-white hover:bg-gray-700"
        >
          <MoreVertical className="h-4 w-4" />
        </Button>
      </div>
      
      <CardContent className="p-6 text-center flex flex-col h-full">
        {/* Bot Icon and Name */}
        <div className="flex flex-col justify-center items-center h-full">
          {/* Bot Icon */}
          <div className="flex justify-center mb-6">
            <div className={`w-20 h-20 ${getTypeColor(bot.type)} rounded-2xl flex items-center justify-center`}>
              {(() => {
                const IconComponent = getTypeIcon(bot.type);
                return <IconComponent className="h-14 w-14 text-white" />;
              })()}
            </div>
          </div>

          {/* Bot Name */}
          <h3 className="font-medium text-white text-lg mb-1">{bot.name}</h3>
        </div>
      </CardContent>
    </Card>
  );
};