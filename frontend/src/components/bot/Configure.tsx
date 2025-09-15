import { Settings } from "lucide-react";

export const Configure = () => {
  return (
    <div className="text-gray-400 text-center py-12">
      <div className="mb-4">
        <Settings className="h-12 w-12 mx-auto text-gray-500" />
      </div>
      <p>Configure content will be displayed here</p>
    </div>
  );
};
