import { Check, Edit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Functionality {
  id: string;
  name: string;
  enabled: boolean;
}

interface OverviewProps {
  functionalities: Functionality[];
  functionalitiesConfirmed: boolean;
  isEditing: boolean;
  toggleFunctionality: (id: string) => void;
  confirmFunctionalities: () => void;
  editFunctionalities: () => void;
}

export const Overview = ({
  functionalities,
  functionalitiesConfirmed,
  isEditing,
  toggleFunctionality,
  confirmFunctionalities,
  editFunctionalities
}: OverviewProps) => {
  return (
    <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
      <CardHeader>
        <CardTitle className="text-white">Select & Confirm Functionalities</CardTitle>
      </CardHeader>
      <CardContent>
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-gray-400 text-sm">Select the functionalities you want your bot to have</p>
            {functionalitiesConfirmed && !isEditing && (
              <Button
                onClick={editFunctionalities}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2 border-gray-600 text-gray-400 hover:text-white hover:border-gray-500"
              >
                <Edit className="h-3 w-3" />
                <span>Edit</span>
              </Button>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
            {functionalities.map((func) => (
              <div 
                key={func.id}
                onClick={() => toggleFunctionality(func.id)}
                className={`flex items-center space-x-3 p-3 rounded-lg border transition-colors ${
                  functionalitiesConfirmed && !isEditing
                    ? 'border-gray-600/50 cursor-not-allowed opacity-70'
                    : 'border-gray-600 hover:border-gray-500 cursor-pointer'
                }`}
              >
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                  func.enabled 
                    ? 'bg-green-600 border-green-600' 
                    : 'border-gray-500 hover:border-gray-400'
                }`}>
                  {func.enabled && <Check className="h-3 w-3 text-white" />}
                </div>
                <span className={`text-sm ${func.enabled ? 'text-white' : 'text-gray-400'}`}>
                  {func.name}
                </span>
              </div>
            ))}
          </div>

          {(!functionalitiesConfirmed || isEditing) && (
            <div className="flex justify-end">
              <Button
                onClick={confirmFunctionalities}
                className="bg-red-800 hover:bg-red-900 text-white px-6"
              >
                Confirm Functionalities
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
