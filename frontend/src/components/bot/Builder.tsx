import React, { useRef, useState, useEffect } from "react";
import { Wrench, UploadCloud, FileText, Loader2, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

interface BuilderProps {
  botId?: string;
}

export const Builder: React.FC<BuilderProps> = ({ botId }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState<string[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [trainStatus, setTrainStatus] = useState<"idle" | "training" | "success" | "error">("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Fetch uploaded docs for this bot
  useEffect(() => {
    if (!botId) return;
    setLoadingDocs(true);
    fetch(`/admin/bots/${botId}/knowledge-base`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    })
      .then((res) => res.json())
      .then((docs) => setUploadedDocs(docs))
      .catch(() => setUploadedDocs([]))
      .finally(() => setLoadingDocs(false));
  }, [botId, uploading]);

  // Handle file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !botId) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("bot_id", String(Number(botId)));
    try {
      const res = await fetch("/admin/upload-document", {
        method: "POST",
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        body: formData,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || data.success === false) {
        throw new Error(data.error || data.detail || "Upload failed");
      }
      toast({ title: "Upload successful", description: file.name, variant: "default" });
    } catch (err) {
      toast({ title: "Upload failed", description: (err as Error).message, variant: "destructive" });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // Handle train model
  const handleTrainModel = async () => {
    setTrainStatus("training");
    try {
      // Simulate API call to train model for this bot
      await new Promise((resolve) => setTimeout(resolve, 2000));
      setTrainStatus("success");
      toast({ title: "Model trained!", description: `Bot ${botId} is now using the latest knowledge base.` });
    } catch {
      setTrainStatus("error");
      toast({ title: "Training failed", description: "Please try again.", variant: "destructive" });
    } finally {
      setTimeout(() => setTrainStatus("idle"), 2000);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wrench className="h-5 w-5" />
            Bot Builder
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Upload Knowledge Base</h3>
            <div className="flex items-center gap-3">
              <input
                type="file"
                accept=".pdf,.txt,.doc,.docx"
                ref={fileInputRef}
                onChange={handleFileUpload}
                className="hidden"
                id="kb-upload"
                disabled={uploading}
              />
              <label htmlFor="kb-upload">
                <Button asChild disabled={uploading} variant="outline">
                  <span className="flex items-center gap-2">
                    <UploadCloud className="h-4 w-4" />
                    {uploading ? "Uploading..." : "Upload Document"}
                  </span>
                </Button>
              </label>
              <span className="text-xs text-gray-500">(PDF, TXT, DOC, DOCX)</span>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Documents are stored per bot and used to train this bot's knowledge base.
            </div>
          </div>

          <div className="mb-6">
            <h3 className="font-semibold mb-2">Knowledge Base Documents</h3>
            {loadingDocs ? (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="animate-spin h-4 w-4" /> Loading documents...
              </div>
            ) : uploadedDocs.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {uploadedDocs.map((doc) => (
                  <Badge key={doc} variant="outline" className="flex items-center gap-1">
                    <FileText className="h-3 w-3" /> {doc}
                  </Badge>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-500">
                <AlertTriangle className="h-4 w-4" /> No documents uploaded yet.
              </div>
            )}
          </div>

          <div className="mb-2">
            <h3 className="font-semibold mb-2">Train Model</h3>
            <Button onClick={handleTrainModel} disabled={trainStatus === "training"}>
              {trainStatus === "training" ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="animate-spin h-4 w-4" /> Training...
                </span>
              ) : trainStatus === "success" ? (
                <span className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="h-4 w-4" /> Trained!
                </span>
              ) : trainStatus === "error" ? (
                <span className="flex items-center gap-2 text-red-600">
                  <AlertTriangle className="h-4 w-4" /> Error
                </span>
              ) : (
                "Train Model with Knowledge Base"
              )}
            </Button>
            <div className="text-xs text-gray-500 mt-2">
              This will update the AI model for <b>only this bot</b> to use the latest uploaded knowledge base.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
