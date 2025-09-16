import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { userAPI, tokenManager } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const UserDashboard = () => {
  const [userEmail, setUserEmail] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Check authentication and get user info
  useEffect(() => {
    const checkAuth = async () => {
      if (!tokenManager.isAuthenticated()) {
        navigate("/user");
        return;
      }

      try {
        const userInfo = await userAPI.getCurrentUser();
        setUserEmail(userInfo.email);
      } catch (error) {
        console.error("Failed to get user info:", error);
        toast({
          title: "Error",
          description: "Failed to load user information",
          variant: "destructive",
        });
        // If token is invalid, redirect to login
        tokenManager.removeToken();
        navigate("/user");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [navigate, toast]);

  const handleLogout = () => {
    tokenManager.removeToken();
    toast({
      title: "Success",
      description: "Logged out successfully!",
    });
    navigate("/");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black relative">
      {/* Header */}
      <div className="flex justify-center w-full pt-4 px-4">
        <header className="flex items-center justify-between w-full max-w-[1204px] h-[76px] px-8 py-4 overflow-hidden rounded-2xl border border-white/6 shadow-inner" 
                style={{
                  background: 'linear-gradient(137deg, rgba(17, 18, 20, .75) 4.87%, rgba(12, 13, 15, .9) 75.88%)',
                  backdropFilter: 'blur(5px)',
                  WebkitBackdropFilter: 'blur(5px)',
                  boxShadow: 'inset 0 1px 1px 0 hsla(0, 0%, 100%, .15)'
                }}>
          <div className="flex items-center gap-2">
            <button onClick={() => navigate("/")} className="flex items-center gap-2">
              <img 
                src="/logo.jpg" 
                alt="AI Lifebot" 
                className="h-8 object-contain rounded-lg"
              />
            </button>
          </div>
          <nav className="flex items-center gap-6 text-gray-400 text-sm">
            <span className="text-white font-medium">
              Welcome, {userEmail}
            </span>
            <Button 
              onClick={handleLogout}
              variant="ghost" 
              className="text-gray-400 hover:text-white transition-colors bg-transparent hover:bg-transparent p-0 h-auto font-normal text-sm"
            >
              Logout
            </Button>
          </nav>
        </header>
      </div>

      {/* Main Content */}
      <div className="flex items-center justify-center p-4" style={{ minHeight: 'calc(100vh - 120px)' }}>
        <div className="text-center space-y-8 max-w-2xl">
          {/* Logo */}
          <div className="flex items-center justify-center mb-12">
            <img 
              src="/logo.jpg" 
              alt="AI Lifebot" 
              className="h-20 object-contain rounded-2xl shadow-lg"
            />
          </div>

          {/* Welcome Content */}
          <div className="space-y-6">
            <h1 className="text-5xl font-bold text-white">
              Welcome to AI Lifebot
            </h1>
            <p className="text-xl text-gray-400 max-w-lg mx-auto leading-relaxed">
              Hello <span className="text-blue-400 font-medium">{userEmail}</span>! 
              You're successfully logged in. Explore our AI chatbot features and enhance your digital experience.
            </p>
          </div>
          
          {/* Dashboard Actions */}
          <div className="space-y-6 pt-8">
            <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-4">User Dashboard</h2>
              <p className="text-gray-400 mb-6">
                Your account is active and ready to use. More features coming soon!
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-2">Account Status</h3>
                  <p className="text-green-400 font-medium">✓ Active</p>
                </div>
                
                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-2">Email</h3>
                  <p className="text-gray-300">{userEmail}</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={() => navigate("/")}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-medium transition-colors"
              >
                Explore Features
              </Button>
              
              <Button 
                onClick={handleLogout}
                variant="outline"
                className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white px-8 py-3 rounded-xl font-medium transition-colors"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;