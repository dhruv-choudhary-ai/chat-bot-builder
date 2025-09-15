import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";

export const PublicNavbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isLoginPage = location.pathname === "/login";
  const isSignupPage = location.pathname === "/signup";

  return (
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
        <nav className="hidden md:flex items-center gap-6 text-gray-400 text-sm">
          <button 
            onClick={() => navigate("/")}
            className="hover:text-white transition-colors"
          >
            Home
          </button>
          <a href="#" className="hover:text-white transition-colors">Bots</a>
          <a href="#" className="hover:text-white transition-colors">Pricing</a>
          <a href="#" className="hover:text-white transition-colors">Help</a>
          <span className="text-gray-600">|</span>
          {!isLoginPage && (
            <Button 
              onClick={() => navigate("/login")}
              variant="ghost" 
              className="text-gray-400 hover:text-white transition-colors bg-transparent hover:bg-transparent p-0 h-auto font-normal text-sm"
            >
              Log in
            </Button>
          )}
          {!isSignupPage && (
            <Button 
              onClick={() => navigate("/signup")}
              className="bg-white text-black hover:bg-gray-200 text-sm px-4 py-2 rounded-lg"
            >
              Sign Up
            </Button>
          )}
        </nav>
      </header>
    </div>
  );
};
