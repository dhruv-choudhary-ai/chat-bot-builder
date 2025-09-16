import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PublicNavbar } from "@/components/layout/PublicNavbar";
import { userAPI, tokenManager } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const User = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Redirect if already authenticated
  useEffect(() => {
    if (tokenManager.isAuthenticated()) {
      navigate("/chat");
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast({
        title: "Error",
        description: "Please enter both email and password",
        variant: "destructive",
      });
      return;
    }

    if (!isLogin && !phoneNumber) {
      toast({
        title: "Error",
        description: "Please enter your phone number",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      if (isLogin) {
        // User login
        const response = await userAPI.login(email, password);
        tokenManager.setToken(response.access_token);
        
        toast({
          title: "Success",
          description: "Logged in successfully!",
        });
      } else {
        // User registration
        const response = await userAPI.register({
          email,
          password,
          phone_number: phoneNumber,
        });
        tokenManager.setToken(response.access_token);
        
        toast({
          title: "Success",
          description: "Account created successfully!",
        });
      }
      
      navigate("/chat");
    } catch (error) {
      toast({
        title: isLogin ? "Login Failed" : "Registration Failed",
        description: error instanceof Error ? error.message : "Please check your information",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setEmail("");
    setPassword("");
    setPhoneNumber("");
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    resetForm();
  };

  return (
    <div className="min-h-screen bg-black relative">
      <PublicNavbar />

      <div className="flex items-center justify-center p-4" style={{ minHeight: 'calc(100vh - 120px)' }}>
        <div className="w-full max-w-md space-y-8">
          {/* Header */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white">
              {isLogin ? "Welcome Back" : "Create Account"}
            </h2>
            <p className="mt-2 text-gray-400">
              {isLogin 
                ? "Sign in to your account to continue" 
                : "Join us and start using AI chatbots"
              }
            </p>
          </div>

          {/* Form */}
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-2xl p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                  Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500"
                  placeholder="Enter your password"
                  required
                />
              </div>

              {!isLogin && (
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <Input
                    id="phone"
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500"
                    placeholder="Enter your phone number"
                    required
                  />
                </div>
              )}

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium transition-colors"
              >
                {isLoading 
                  ? (isLogin ? "Signing In..." : "Creating Account...") 
                  : (isLogin ? "Sign In" : "Create Account")
                }
              </Button>
            </form>

            {/* Toggle between login and register */}
            <div className="mt-6 text-center">
              <p className="text-gray-400">
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <button
                  type="button"
                  onClick={toggleMode}
                  className="ml-2 text-blue-400 hover:text-blue-300 transition-colors font-medium"
                >
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>

            {/* Admin login link */}
            <div className="mt-4 text-center">
              <p className="text-gray-500 text-sm">
                Looking for admin access?
                <button
                  type="button"
                  onClick={() => navigate("/login")}
                  className="ml-2 text-gray-400 hover:text-gray-300 transition-colors underline"
                >
                  Admin Login
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default User;