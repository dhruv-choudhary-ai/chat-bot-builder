import { useState, useRef, useEffect } from "react";
import { Search, Bell, User, Settings, LogOut, UserCircle} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { authAPI, tokenManager, type AdminInfo } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export const Navbar = () => {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [adminInfo, setAdminInfo] = useState<AdminInfo | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Load admin info
  useEffect(() => {
    const loadAdminInfo = async () => {
      try {
        if (tokenManager.isAuthenticated()) {
          const admin = await authAPI.getCurrentAdmin();
          setAdminInfo(admin);
        }
      } catch (error) {
        console.error('Failed to load admin info:', error);
      }
    };

    loadAdminInfo();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    toast({
      title: "Logged out",
      description: "You have been successfully logged out.",
    });
    navigate('/login');
  };

  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    if (email) {
      return email.slice(0, 2).toUpperCase();
    }
    return 'AD';
  };

  return (
    <nav className="border-b border-border bg-card">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <button 
            onClick={() => navigate("/admin")}
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
          >
            <img 
              src="/logo.jpg" 
              alt="AI Lifebot" 
              className="h-8 object-contain rounded-lg"
            />
          </button>

          {/* Search Bar */}
          <div className="flex-1 max-w-4xl mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search"
                className="pl-10 bg-input border-border text-foreground placeholder:text-muted-foreground w-full rounded-xl"
              />
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Bell className="h-5 w-5" />
            </Button>
            
            <div className="w-px h-6 bg-border" />
            
            {/* User Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-secondary text-foreground text-sm">
                    {adminInfo ? getInitials(adminInfo.name, adminInfo.email) : <User className="h-4 w-4" />}
                  </AvatarFallback>
                </Avatar>
              </button>

              {/* Dropdown Menu */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-black rounded-lg shadow-lg border border-gray-800 py-2 z-50">
                  {/* User Info */}
                  <div className="px-4 py-3 border-b border-gray-800">
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="bg-blue-500 text-white">
                          {adminInfo ? getInitials(adminInfo.name, adminInfo.email) : 'AD'}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium text-white">
                          {adminInfo?.name || 'Admin User'}
                        </p>
                        <p className="text-xs text-gray-400">
                          {adminInfo?.email || 'admin@example.com'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Menu Items */}
                  <div className="py-1">
                    <button
                      onClick={() => {
                        navigate('/admin/profile');
                        setIsDropdownOpen(false);
                      }}
                      className="flex items-center space-x-3 w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 transition-colors"
                    >
                      <UserCircle className="h-4 w-4" />
                      <span>Profile</span>
                    </button>
                    
                    <button
                      onClick={() => {
                        navigate('/admin/settings');
                        setIsDropdownOpen(false);
                      }}
                      className="flex items-center space-x-3 w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 transition-colors"
                    >
                      <Settings className="h-4 w-4" />
                      <span>Settings</span>
                    </button>
                  </div>

                  {/* Logout */}
                  <div className="border-t border-gray-800 pt-1">
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsDropdownOpen(false);
                      }}
                      className="flex items-center space-x-3 w-full px-4 py-2 text-sm text-red-400 hover:bg-gray-800 transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Sign out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};