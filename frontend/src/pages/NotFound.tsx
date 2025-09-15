import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Home } from "lucide-react";

const NotFound = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gradient-bg flex items-center justify-center p-4">
      <div className="text-center space-y-6">
        <div className="flex items-center justify-center mb-8">
          <img 
            src="/logo.jpg" 
            alt="AI Lifebot" 
            className="h-12 object-contain rounded-lg mr-3"
          />
          {/* <h1 className="text-3xl font-bold text-foreground">AI Lifebot</h1> */}
        </div>
        
        <div className="space-y-4">
          <h2 className="text-6xl font-bold text-primary">404</h2>
          <h3 className="text-2xl font-semibold text-foreground">Page Not Found</h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>
        
        <Button 
          onClick={() => navigate("/")}
          className="bg-gradient-primary hover:shadow-glow transition-all duration-300 font-medium"
        >
          <Home className="mr-2 h-4 w-4" />
          Return Home
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
