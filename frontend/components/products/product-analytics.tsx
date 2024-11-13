

import { Product } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart3, RefreshCw, Star } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import SentimentSummary from "@/components/products/sentiment-summary"

interface ProductAnalyticsProps {
  product: Product;
}

interface SentimentData {
  product_id: number;
  positive_reviews: number;
  negative_reviews: number;
  neutral_reviews: number;
  average_rating: number;
  most_rating: number;
  word_frequencies: { word: string; frequency: number }[];
  word_cloud: string;
  word_clouds?: { platform: string; word_cloud: string }[];
}

export function ProductAnalytics({ product }: ProductAnalyticsProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [sentimentDataAmazon, setSentimentDataAmazon] = useState<SentimentData | null>(null);
  const [sentimentDataFlipkart, setSentimentDataFlipkart] = useState<SentimentData | null>(null);

  const analyzeSentiment = async (platform: string) => {
    setAnalyzing(true);
    try {
      const response = await fetch(
        `/api/reviews/analyse/${product.id}?platform=${platform.toLowerCase()}`,
        { method: "POST" }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Analysis failed");
      }
      
      const data = await response.json();
      toast.success(data.message || "Analysis completed successfully");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to analyze reviews"
      );
    } finally {
      setAnalyzing(false);
    }
  };

  // Fetch sentiment data for Amazon and Flipkart platforms on load
  useEffect(() => {
    const fetchSentimentData = async (platform: string) => {
      try {
        const response = await fetch(
          `/api/sentiment_summary/${product.id}?platform=${platform.toLowerCase()}`,
          { method: "GET" }
        );

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || "Analysis failed");
        }

        const data = await response.json();
        console.log(JSON.stringify(data,null,2))

        if (platform.toLowerCase() === "amazon") {
          setSentimentDataAmazon(data);
        } else if (platform.toLowerCase() === "flipkart") {
          setSentimentDataFlipkart(data);
        }
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to fetch sentiment data");
      }
    };

    // Fetch for both Amazon and Flipkart
    fetchSentimentData("amazon");
    fetchSentimentData("flipkart");
  }, [product.id]);

  return (
    <>
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


<div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 mb-4">
{/* Amazon Sentiment */}
<div className="flex justify-center items-center min-h-full">
    {sentimentDataAmazon ? (
      <SentimentSummary sentimentData={sentimentDataAmazon} />
    ) : (
      <div className="flex justify-center items-center text-gray-800">
        <Card>No sentiment summary found for Amazon</Card>
        
      </div>
    )}
  </div>

  {/* Flipkart Sentiment */}
  <Card className="flex justify-center items-start min-h-full p-6">
    {sentimentDataFlipkart ? (
      <SentimentSummary sentimentData={sentimentDataFlipkart} />
    ) : (
      <div className="flex justify-center items-start text-gray-800">
        No Sentiment Summary found for Flipkart
      </div>
    )}
  </Card>
</div>
    </>
  );
}
