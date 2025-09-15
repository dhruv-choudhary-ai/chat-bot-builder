import { Check, Play, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Functionality {
  id: string;
  name: string;
  enabled: boolean;
}

interface BotStatus {
  trained: boolean;
  deployed: boolean;
}

interface BotManagementProps {
  functionalities: Functionality[];
  functionalitiesConfirmed: boolean;
  botStatus: BotStatus;
  handleTrainBot: () => void;
  handleDeployBot: () => void;
}

export const BotManagement = ({
  functionalities,
  functionalitiesConfirmed,
  botStatus,
  handleTrainBot,
  handleDeployBot
}: BotManagementProps) => {
  return (
    <>
      {/* Training & Deployment */}
      <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className={`border-none ${!functionalitiesConfirmed ? 'opacity-50' : ''}`}>
        <CardHeader className="pb-4">
          <CardTitle className="text-white text-lg font-semibold">Bot Management</CardTitle>
          <p className="text-gray-400 text-sm mt-1">
            {!functionalitiesConfirmed ? 'Confirm functionalities first' : 'Train and deploy your bot'}
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Train Bot Section */}
          <div className={`p-4 rounded-lg border border-gray-600/30 bg-gray-800/20 ${!functionalitiesConfirmed ? 'pointer-events-none' : ''}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  !functionalitiesConfirmed ? 'bg-gray-600' :
                  botStatus.trained ? 'bg-green-600' : 'bg-blue-600'
                }`}>
                  {botStatus.trained ? <Check className="h-4 w-4 text-white" /> : <Play className="h-4 w-4 text-white" />}
                </div>
                <div>
                  <h4 className="text-white font-medium text-sm">Training</h4>
                  <p className="text-gray-400 text-xs">Prepare your bot with data</p>
                </div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                !functionalitiesConfirmed ? 'bg-gray-600/20 text-gray-400' :
                botStatus.trained ? 'bg-green-600/20 text-green-400' : 'bg-blue-600/20 text-blue-400'
              }`}>
                {!functionalitiesConfirmed ? 'Locked' : botStatus.trained ? 'Complete' : 'Ready'}
              </div>
            </div>
            <Button
              onClick={handleTrainBot}
              disabled={!functionalitiesConfirmed || botStatus.trained}
              className={`w-full h-10 ${
                !functionalitiesConfirmed ? 'bg-gray-600/20 text-gray-500 cursor-not-allowed' :
                botStatus.trained 
                  ? 'bg-green-600/20 hover:bg-green-600/30 text-green-400' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              } border-0`}
              variant={botStatus.trained ? "outline" : "default"}
            >
              {!functionalitiesConfirmed ? 'Confirm Functionalities First' : 
               botStatus.trained ? 'Training Complete' : 'Start Training'}
            </Button>
          </div>

          {/* Deploy Bot Section */}
          <div className={`p-4 rounded-lg border border-gray-600/30 bg-gray-800/20 ${!functionalitiesConfirmed ? 'pointer-events-none' : ''}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  !functionalitiesConfirmed ? 'bg-gray-600' :
                  botStatus.deployed ? 'bg-green-600' : !botStatus.trained ? 'bg-gray-600' : 'bg-red-800'
                }`}>
                  <Rocket className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h4 className="text-white font-medium text-sm">Deployment</h4>
                  <p className="text-gray-400 text-xs">Make your bot live</p>
                </div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                !functionalitiesConfirmed ? 'bg-gray-600/20 text-gray-400' :
                botStatus.deployed 
                  ? 'bg-green-600/20 text-green-400' 
                  : !botStatus.trained 
                    ? 'bg-gray-600/20 text-gray-400' 
                    : 'bg-red-800/20 text-red-400'
              }`}>
                {!functionalitiesConfirmed ? 'Locked' :
                 botStatus.deployed ? 'Live' : !botStatus.trained ? 'Pending' : 'Ready'}
              </div>
            </div>
            <Button
              onClick={handleDeployBot}
              disabled={!functionalitiesConfirmed || !botStatus.trained || botStatus.deployed}
              className={`w-full h-10 ${
                !functionalitiesConfirmed ? 'bg-gray-600/20 text-gray-500 cursor-not-allowed' :
                botStatus.deployed 
                  ? 'bg-green-600/20 hover:bg-green-600/30 text-green-400'
                  : !botStatus.trained 
                    ? 'bg-gray-600/20 text-gray-500 cursor-not-allowed' 
                    : 'bg-red-800 hover:bg-red-900 text-white'
              } border-0`}
              variant={botStatus.deployed ? "outline" : "default"}
            >
              {!functionalitiesConfirmed ? 'Confirm Functionalities First' :
               botStatus.deployed 
                ? 'Successfully Deployed' 
                : !botStatus.trained 
                  ? 'Complete Training First' 
                  : 'Deploy to Production'
              }
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Bot Status */}
      <Card style={{ backgroundColor: 'hsl(230, 5%, 15%)' }} className="border-none">
        <CardHeader>
          <CardTitle className="text-white text-sm">Bot Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Active Functionalities</span>
            <span className="text-white font-medium">
              {functionalities.filter(f => f.enabled).length}/{functionalities.length}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Training Status</span>
            <span className={`font-medium ${botStatus.trained ? 'text-green-400' : 'text-yellow-400'}`}>
              {botStatus.trained ? 'Complete' : 'Pending'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Deployment Status</span>
            <span className={`font-medium ${botStatus.deployed ? 'text-green-400' : 'text-gray-400'}`}>
              {botStatus.deployed ? 'Live' : 'Not Deployed'}
            </span>
          </div>
        </CardContent>
      </Card>
    </>
  );
};
