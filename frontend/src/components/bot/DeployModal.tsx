import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ChatbotPreview } from "./ChatbotPreview";
import { Download, Copy, Eye, Settings, Code, Globe } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DeployModalProps {
  isOpen: boolean;
  onClose: () => void;
  botInfo: {
    id: number;
    name: string;
    bot_type: string;
  };
}

export const DeployModal = ({ isOpen, onClose, botInfo }: DeployModalProps) => {
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#3B82F6");
  const [position, setPosition] = useState<"bottom-right" | "bottom-left">("bottom-right");
  const [greeting, setGreeting] = useState(`Hi! I'm ${botInfo.name}, your ${botInfo.bot_type.toLowerCase()} assistant. How can I help you today?`);
  const { toast } = useToast();

  const generateEmbedCode = () => {
    const config = {
      botId: botInfo.id,
      botName: botInfo.name,
      botType: botInfo.bot_type,
      primaryColor,
      position,
      greeting,
      apiUrl: "http://localhost:8000" // This should be your production API URL
    };

    return `<!-- LifeBot Chatbot Integration -->
<script>
  (function() {
    // LifeBot Configuration
    window.LifeBotConfig = ${JSON.stringify(config, null, 2)};
    
    // Create chatbot container
    const createChatbot = () => {
      const chatbotContainer = document.createElement('div');
      chatbotContainer.id = 'lifebot-chatbot';
      chatbotContainer.innerHTML = \`
        <div id="lifebot-widget" style="
          position: fixed;
          ${position}: 20px;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        ">
          <div id="lifebot-button" style="
            width: 56px;
            height: 56px;
            background-color: ${primaryColor};
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: transform 0.2s;
          " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
            </svg>
          </div>
          <div id="lifebot-chat" style="
            display: none;
            width: 320px;
            height: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 28px rgba(0,0,0,0.12);
            position: absolute;
            bottom: 70px;
            ${position === 'bottom-right' ? 'right: 0' : 'left: 0'};
            overflow: hidden;
          ">
            <div style="
              background: ${primaryColor};
              color: white;
              padding: 16px;
              display: flex;
              align-items: center;
              justify-content: space-between;
            ">
              <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
                  </svg>
                </div>
                <div>
                  <div style="font-weight: 500; font-size: 14px;">${botInfo.name}</div>
                  <div style="font-size: 12px; opacity: 0.8;">Online</div>
                </div>
              </div>
              <button id="lifebot-close" style="
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
              " onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <div id="lifebot-messages" style="
              height: 280px;
              overflow-y: auto;
              padding: 16px;
              background: #f8f9fa;
            ">
              <div style="
                background: white;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 12px;
                max-width: 80%;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
              ">
                ${greeting}
              </div>
            </div>
            <div style="
              padding: 16px;
              border-top: 1px solid #e9ecef;
              display: flex;
              gap: 8px;
            ">
              <input id="lifebot-input" type="text" placeholder="Type your message..." style="
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 20px;
                outline: none;
                font-size: 14px;
              ">
              <button id="lifebot-send" style="
                background: ${primaryColor};
                color: white;
                border: none;
                border-radius: 50%;
                width: 36px;
                height: 36px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
              ">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22,2 15,22 11,13 2,9"></polygon>
                </svg>
              </button>
            </div>
          </div>
        </div>
      \`;
      document.body.appendChild(chatbotContainer);

      // Event listeners
      const button = document.getElementById('lifebot-button');
      const chat = document.getElementById('lifebot-chat');
      const closeBtn = document.getElementById('lifebot-close');
      const input = document.getElementById('lifebot-input');
      const sendBtn = document.getElementById('lifebot-send');
      const messages = document.getElementById('lifebot-messages');

      button.addEventListener('click', () => {
        chat.style.display = chat.style.display === 'none' ? 'block' : 'none';
      });

      closeBtn.addEventListener('click', () => {
        chat.style.display = 'none';
      });

      const sendMessage = () => {
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        const userMsg = document.createElement('div');
        userMsg.style.cssText = \`
          background: ${primaryColor};
          color: white;
          padding: 8px 12px;
          border-radius: 8px;
          margin: 8px 0;
          max-width: 80%;
          margin-left: auto;
          text-align: right;
        \`;
        userMsg.textContent = message;
        messages.appendChild(userMsg);

        input.value = '';
        messages.scrollTop = messages.scrollHeight;

        // Simulate bot response
        setTimeout(() => {
          const botMsg = document.createElement('div');
          botMsg.style.cssText = \`
            background: white;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            max-width: 80%;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
          \`;
          botMsg.textContent = "Thanks for your message! I'm processing your request and will get back to you shortly.";
          messages.appendChild(botMsg);
          messages.scrollTop = messages.scrollHeight;
        }, 1000);
      };

      sendBtn.addEventListener('click', sendMessage);
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
      });
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', createChatbot);
    } else {
      createChatbot();
    }
  })();
</script>`;
  };

  const downloadEmbedCode = async () => {
    try {
      const params = new URLSearchParams({
        primary_color: primaryColor,
        position: position,
        greeting: greeting
      });
      
      const response = await fetch(
        `http://localhost:8000/admin/bots/${botInfo.id}/embed-script?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to generate embed script');
      }
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lifebot-${botInfo.id}-embed.js`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Download Started",
        description: "The chatbot embed script has been downloaded successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download embed script. Please try again.",
        variant: "destructive",
      });
    }
  };

  const copyEmbedCode = () => {
    const code = generateEmbedCode();
    navigator.clipboard.writeText(code);
    toast({
      title: "Copied!",
      description: "Embed code copied to clipboard.",
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Deploy {botInfo.name} to Production
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="preview" className="flex-1 overflow-hidden">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="preview" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Preview
            </TabsTrigger>
            <TabsTrigger value="customize" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Customize
            </TabsTrigger>
            <TabsTrigger value="embed" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Get Code
            </TabsTrigger>
          </TabsList>

          <TabsContent value="preview" className="flex-1 relative">
            <Card>
              <CardHeader>
                <CardTitle>Live Preview</CardTitle>
                <p className="text-sm text-muted-foreground">
                  This is how your chatbot will appear on your website
                </p>
              </CardHeader>
              <CardContent>
                <div className="relative h-96 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg overflow-hidden">
                  <div className="absolute inset-0 bg-gray-100 opacity-50"></div>
                  <div className="absolute top-4 left-4 text-gray-600 text-sm">
                    Preview: {websiteUrl || "your-website.com"}
                  </div>
                  <ChatbotPreview
                    botName={botInfo.name}
                    botType={botInfo.bot_type}
                    primaryColor={primaryColor}
                    position={position}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="customize" className="space-y-4 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Appearance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="primaryColor">Primary Color</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Input
                        id="primaryColor"
                        type="color"
                        value={primaryColor}
                        onChange={(e) => setPrimaryColor(e.target.value)}
                        className="w-12 h-10 p-1 border rounded"
                      />
                      <Input
                        value={primaryColor}
                        onChange={(e) => setPrimaryColor(e.target.value)}
                        placeholder="#3B82F6"
                        className="flex-1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Position</Label>
                    <div className="flex gap-2 mt-1">
                      <Button
                        variant={position === "bottom-right" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setPosition("bottom-right")}
                      >
                        Bottom Right
                      </Button>
                      <Button
                        variant={position === "bottom-left" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setPosition("bottom-left")}
                      >
                        Bottom Left
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Behavior</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="greeting">Welcome Message</Label>
                    <textarea
                      id="greeting"
                      value={greeting}
                      onChange={(e) => setGreeting(e.target.value)}
                      className="w-full mt-1 p-2 border rounded-md resize-none h-20"
                      placeholder="Enter the initial greeting message..."
                    />
                  </div>

                  <div>
                    <Label htmlFor="websiteUrl">Website URL (Optional)</Label>
                    <Input
                      id="websiteUrl"
                      value={websiteUrl}
                      onChange={(e) => setWebsiteUrl(e.target.value)}
                      placeholder="https://your-website.com"
                      className="mt-1"
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="embed" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Integration Instructions</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Choose how you want to integrate the chatbot into your website
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button
                    onClick={downloadEmbedCode}
                    className="h-20 flex flex-col items-center gap-2 bg-primary hover:bg-primary/90"
                  >
                    <Download className="h-6 w-6" />
                    <div className="text-center">
                      <div className="font-medium">Download Script</div>
                      <div className="text-xs opacity-80">Get .js file to upload</div>
                    </div>
                  </Button>

                  <Button
                    onClick={copyEmbedCode}
                    variant="outline"
                    className="h-20 flex flex-col items-center gap-2"
                  >
                    <Copy className="h-6 w-6" />
                    <div className="text-center">
                      <div className="font-medium">Copy Code</div>
                      <div className="text-xs opacity-80">Paste in your HTML</div>
                    </div>
                  </Button>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium flex items-center gap-2">
                    <Badge variant="outline">1</Badge>
                    Installation Options
                  </h4>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p><strong>Option A:</strong> Download the script and upload it to your website, then add: <code>&lt;script src="path/to/lifebot-embed.js"&gt;&lt;/script&gt;</code></p>
                    <p><strong>Option B:</strong> Copy the code and paste it directly before the closing <code>&lt;/body&gt;</code> tag in your HTML</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium flex items-center gap-2">
                    <Badge variant="outline">2</Badge>
                    Verification
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    After installation, visit your website and look for the chat button in the {position.replace('-', ' ')} corner.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
