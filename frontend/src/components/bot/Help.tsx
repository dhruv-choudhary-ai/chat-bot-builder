import { HelpCircle } from "lucide-react";

export const Help = () => {
  return (
    <div className="text-gray-400 text-center py-12">
      <div className="mb-4">
        <HelpCircle className="h-12 w-12 mx-auto text-gray-500" />
      </div>
      <p>Help content will be displayed here</p>
    </div>
  );
};
