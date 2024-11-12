import { Product } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface ProductReviewsProps {
  product: Product;
}

export function ProductReviews({ product }: ProductReviewsProps) {
  const [scraping, setScraping] = useState(false);

  const scrapeReviews = async (platform: string, id: string) => {
    setScraping(true);
    try {
      const response = await fetch(
        `/api/scrape_${platform.toLowerCase()}_reviews/${id}`,
        { method: "POST" }
      );
      
      if (!response.ok) throw new Error("Scraping failed");
      
      const data = await response.json();
      toast.success(`Started scraping reviews from ${platform}`);
    } catch (error) {
      toast.error("Failed to start scraping");
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      {product.platforms.map((platform) => (
        <Card key={platform.platform} className="p-6">
          <h3 className="text-lg font-medium mb-4">
            {platform.platform} Reviews
          </h3>
          <div className="space-y-4">
            <Button
              onClick={() => scrapeReviews(platform.platform, platform.id)}
              disabled={scraping}
              className="w-full"
            >
              {scraping ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Scrape Reviews
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}