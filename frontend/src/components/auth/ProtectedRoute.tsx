import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { tokenManager } from "@/lib/api";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!tokenManager.isAuthenticated()) {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  // Show loading or redirect if not authenticated
  if (!tokenManager.isAuthenticated()) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
