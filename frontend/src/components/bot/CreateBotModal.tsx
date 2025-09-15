import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Briefcase, ShoppingCart, GraduationCap, Heart, Zap, MessageSquare, Calculator, BookOpen, Users, Globe } from "lucide-react";

interface CreateBotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateBot: (name: string, type: string) => void;
  availableBotTypes?: string[];
}

// const botTemplates = [
//   { name: "Sales Bot", icon: Briefcase, description: "Customer sales assistant" },
//   { name: "Career Bot", icon: GraduationCap, description: "Career guidance counselor" },
//   { name: "Retail Bot", icon: ShoppingCart, description: "Shopping assistant" },
//   { name: "Health Bot", icon: Heart, description: "Health & wellness guide" },
//   { name: "Support Bot", icon: MessageSquare, description: "Customer support" },
//   { name: "Finance Bot", icon: Calculator, description: "Financial advisor" },
//   { name: "Learning Bot", icon: BookOpen, description: "Educational tutor" },
//   { name: "HR Bot", icon: Users, description: "Human resources assistant" },
//   { name: "Travel Bot", icon: Globe, description: "Travel planning guide" },
//   { name: "Custom Bot", icon: Zap, description: "Build from scratch" },
// ];

export const CreateBotModal = ({ isOpen, onClose, onCreateBot, availableBotTypes = [] }: CreateBotModalProps) => {
  const [step, setStep] = useState<"name" | "template">("name");
  const [botName, setBotName] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  // Map backend bot types to UI templates
  const getTemplateName = (botType: string) => {
    const typeMap: { [key: string]: string } = {
      'banking': 'Banking Bot',
      'career_counselling': 'Career Bot',
      'retail': 'Retail Bot',
      'insurance': 'Insurance Bot',
      'hotel_booking': 'Hotel Bot',
      'telecom': 'Telecom Bot',
      'real_estate': 'Real Estate Bot',
      'lead_capturing': 'Sales Bot',
      'course_enrollment': 'Learning Bot',
    };
    return typeMap[botType] || botType.charAt(0).toUpperCase() + botType.slice(1) + ' Bot';
  };

  // Map bot types to icons and colors
  const getTemplateIcon = (botType: string) => {
    const iconMap: { [key: string]: { icon: any; color: { bg: string; icon: string } } } = {
      'banking': { icon: Calculator, color: { bg: 'bg-green-600', icon: 'text-white' } },
      'career_counselling': { icon: GraduationCap, color: { bg: 'bg-blue-600', icon: 'text-white' } },
      'retail': { icon: ShoppingCart, color: { bg: 'bg-purple-600', icon: 'text-white' } },
      'insurance': { icon: Heart, color: { bg: 'bg-orange-600', icon: 'text-white' } },
      'hotel_booking': { icon: Globe, color: { bg: 'bg-cyan-600', icon: 'text-white' } },
      'telecom': { icon: Zap, color: { bg: 'bg-indigo-600', icon: 'text-white' } },
      'real_estate': { icon: Briefcase, color: { bg: 'bg-pink-600', icon: 'text-white' } },
      'lead_capturing': { icon: Users, color: { bg: 'bg-teal-600', icon: 'text-white' } },
      'course_enrollment': { icon: BookOpen, color: { bg: 'bg-yellow-600', icon: 'text-white' } },
    };
    return iconMap[botType] || { icon: MessageSquare, color: { bg: 'bg-gray-600', icon: 'text-white' } };
  };

  const handleCreateBot = () => {
    if (step === "name" && botName.trim()) {
      setStep("template");
    } else if (step === "template" && selectedTemplate) {
      onCreateBot(botName, selectedTemplate);
      handleClose();
    }
  };

  const handleClose = () => {
    setStep("name");
    setBotName("");
    setSelectedTemplate(null);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className={`${step === "name" ? "max-w-md" : "max-w-4xl"} bg-card border-border`}>
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-foreground">
            {step === "name" ? "Create a bot" : ""}
          </DialogTitle>
        </DialogHeader>

        {step === "name" ? (
          <div className="space-y-4 py-3">
            <div className="space-y-2">
             <Input
                id="bot-name"
                placeholder="Type name"
                value={botName}
                onChange={(e) => setBotName(e.target.value)}
                className="bg-input border-border text-foreground"
              />
            </div>
            
            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={handleClose} className="border-border">
                Cancel
              </Button>
              <Button 
                onClick={handleCreateBot}
                disabled={!botName.trim()}
                className="bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200"
              >
                Create Bot
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-2">
            {/* Custom Bot Canvas */}
            <Card className="border-2 border-dashed border-gray-500/50 bg-gray-800/50 hover:bg-gray-700/50 transition-all duration-200 cursor-pointer group"
                  onClick={() => {
                    setSelectedTemplate("custom");
                    handleCreateBot();
                  }}>
              <CardContent className="flex flex-col items-center justify-center p-6">
                <div className="w-12 h-12 bg-gray-700 rounded-lg flex items-center justify-center mb-3 group-hover:bg-gray-600 transition-all duration-200">
                  <div className="text-gray-400 text-xl font-light">+</div>
                </div>
                <h3 className="font-medium text-white text-center">Blank Bot Canvas</h3>
              </CardContent>
            </Card>

            {/* Section Title */}
            <div className="text-center">
              <h3 className="font-medium text-white mb-2">Available Bot Types</h3>
            </div>

            {/* Bot Templates Grid */}
            <div className="grid grid-cols-6 gap-3 max-h-48 overflow-y-auto">
              {availableBotTypes.map((botType) => {
                const templateInfo = getTemplateIcon(botType);
                const IconComponent = templateInfo.icon;
                const colors = templateInfo.color;
                const displayName = getTemplateName(botType);
                const isSelected = selectedTemplate === botType;
                
                return (
                  <Card 
                    key={botType}
                    className={`cursor-pointer transition-all duration-200 border-gray-600 hover:border-gray-400 bg-gray-800 hover:bg-gray-700 ${
                      isSelected ? 'border-green-500 ring-4 ring-green-500/20 border-4' : ''
                    }`}
                    onClick={() => setSelectedTemplate(botType)}
                  >
                    <CardContent className="p-3 text-center">
                      <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center mx-auto mb-2`}>
                        <IconComponent className={`h-5 w-5 ${colors.icon}`} />
                      </div>
                      <h4 className="font-medium text-white text-xs mb-1">{displayName}</h4>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
            
            {/* Bottom Section */}
            <div className="border-t border-gray-700 pt-3">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-300 font-medium">Quickstart with a template</p>
                  <p className="text-xs text-gray-400">Choose a template to quick start or start with a blank bot canvas</p>
                </div>
                <div className="flex space-x-3">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep("name")} 
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleCreateBot}
                    disabled={!selectedTemplate}
                    className="bg-red-600 text-white hover:bg-red-700 transition-all duration-200 disabled:opacity-50"
                  >
                    Create Bot
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};