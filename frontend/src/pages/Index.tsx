import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { PublicNavbar } from "@/components/layout/PublicNavbar";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black relative">
      <PublicNavbar />

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

          {/* Hero Content */}
          <div className="space-y-6">
            <h1 className="text-5xl font-bold text-white">
              Welcome to AI Lifebot
            </h1>
            <p className="text-xl text-gray-400 max-w-lg mx-auto leading-relaxed">
              Create intelligent chatbots that enhance your business and personal life. 
              Build, deploy, and manage AI assistants with ease.
            </p>
          </div>
          
          {/* Call to Action */}
          <div className="space-y-6 pt-8">
            <Button 
              onClick={() => navigate("/signup")} 
              className="bg-white text-black hover:bg-gray-100 transition-all duration-200 text-lg px-12 py-4 h-auto font-medium rounded-xl"
            >
              Get Started Free
            </Button>
            
            <div className="text-center">
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
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-16">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-gray-800 rounded-xl flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">Fast Setup</h3>
              <p className="text-gray-400 text-sm">Create your first bot in minutes with our intuitive interface</p>
            </div>
            
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-gray-800 rounded-xl flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">Smart AI</h3>
              <p className="text-gray-400 text-sm">Powered by advanced AI models for natural conversations</p>
            </div>
            
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-gray-800 rounded-xl flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">Easy to Use</h3>
              <p className="text-gray-400 text-sm">No coding required. Deploy and manage bots effortlessly</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
