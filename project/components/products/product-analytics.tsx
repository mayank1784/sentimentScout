import { Product } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart3, RefreshCw } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface ProductAnalyticsProps {
  product: Product;
}

export function ProductAnalytics({ product }: ProductAnalyticsProps) {
  const [analyzing, setAnalyzing] = useState(false);

  const analyzeSentiment = async (platform: string) => {
    setAnalyzing(true);
    try {
      const response = await fetch(
        `/api/reviews/analyse/${product.id}?platform=${platform}`,
        { method: "POST" }
      );
      
      if (!response.ok) throw new Error("Analysis failed");
      
      const data = await response.json();
      toast.success("Analysis completed successfully");
    } catch (error) {
      toast.error("Failed to analyze reviews");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      {product.platforms.map((platform) => (
        <Card key={platform.platform} className="p-6">
          <h3 className="text-lg font-medium mb-4">
            {platform.platform} Analysis
          </h3>
          <div className="space-y-4">
            <Button
              onClick={() => analyzeSentiment(platform.platform.toLowerCase())}
              disabled={analyzing}
              className="w-full"
            >
              {analyzing ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <BarChart3 className="mr-2 h-4 w-4" />
              )}
              Analyze Reviews
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}