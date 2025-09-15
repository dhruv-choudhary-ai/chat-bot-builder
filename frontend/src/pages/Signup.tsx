import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PublicNavbar } from "@/components/layout/PublicNavbar";
import { authAPI, tokenManager } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Signup = () => {
  const [name, setName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Redirect if already authenticated
  useEffect(() => {
    if (tokenManager.isAuthenticated()) {
      navigate("/admin");
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !phoneNumber || !email || !password) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await authAPI.signup({
        email,
        password,
        name,
        phone_number: phoneNumber,
      });
      
      tokenManager.setToken(response.access_token);
      
      toast({
        title: "Success",
        description: response.msg || "Account created successfully!",
      });
      
      navigate("/admin");
    } catch (error) {
      toast({
        title: "Signup Failed",
        description: error instanceof Error ? error.message : "Failed to create account",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black relative">
      <PublicNavbar />

      {/* Main Content */}
      <div className="flex items-center justify-center p-4" style={{ minHeight: 'calc(100vh - 120px)' }}>
        <div className="w-full max-w-sm">
          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-semibold text-white pt-4">Create your Account</h1>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4 mb-6">
            <Input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
              className="h-12 bg-gray-800 border-gray-700 text-white placeholder:text-gray-400 focus:border-gray-500 rounded-xl"
              required
            />
            <Input
              type="tel"
              placeholder="Phone Number (e.g., +1234567890)"
              value={phoneNumber}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPhoneNumber(e.target.value)}
              className="h-12 bg-gray-800 border-gray-700 text-white placeholder:text-gray-400 focus:border-gray-500 rounded-xl"
              required
            />
            <Input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              className="h-12 bg-gray-800 border-gray-700 text-white placeholder:text-gray-400 focus:border-gray-500 rounded-xl"
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              className="h-12 bg-gray-800 border-gray-700 text-white placeholder:text-gray-400 focus:border-gray-500 rounded-xl"
              required
            />
            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full h-12 bg-white text-black hover:bg-gray-100 font-medium rounded-xl disabled:opacity-50"
            >
              {isLoading ? "Creating Account..." : "Create Account"}
            </Button>
          </form>

          {/* Sign up link */}
          <div className="text-center mb-6">
            <span className="text-gray-400 text-sm">
              Already have an account?{" "}
              <button 
                onClick={() => navigate("/login")}
                className="text-gray-300 hover:text-white transition-colors underline bg-transparent border-none cursor-pointer"
              >
                Sign in →
              </button>
            </span>
          </div>

          {/* Separator */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-black text-gray-400">or</span>
            </div>
          </div>

          {/* Social Login Buttons */}
          <div className="flex gap-3 justify-center">
            <Button 
              variant="outline" 
              className="w-12 h-12 bg-gray-800 border-gray-700 hover:bg-gray-700 text-white flex items-center justify-center rounded-xl p-0"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
            </Button>

            <Button 
              variant="outline" 
              className="w-12 h-12 bg-gray-800 border-gray-700 hover:bg-gray-700 text-white flex items-center justify-center rounded-xl p-0"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/>
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
