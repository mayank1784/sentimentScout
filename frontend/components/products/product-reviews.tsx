import { Product } from "@/lib/types";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableRow,
  TableCell,
  TableHeader,
  TableBody,
} from "@/components/ui/table";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { ChevronUp, ChevronDown } from "lucide-react";

interface SortArrowProps {
  direction: "asc" | "desc";
}

const SortArrow = ({ direction }: SortArrowProps) => {
  return direction === "asc" ? (
    <ChevronUp className="ml-1 h-4 w-4" />
  ) : (
    <ChevronDown className="ml-1 h-4 w-4" />
  );
};

interface ProductReviewsProps {
  product: Product;
}

export function ProductReviews({ product }: ProductReviewsProps) {
  const [reviews, setReviews] = useState<any[]>([]);
  const [filteredReviews, setFilteredReviews] = useState<any[]>([]);
  const [sorting, setSorting] = useState<{
    key: string;
    direction: "asc" | "desc";
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    platform: "all",
    sentiment: "all",
    rating: "all",
  });
  const [scraping, setScraping] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  // Fetch all reviews once
  useEffect(() => {
    const fetchReviews = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/product/${product.id}/reviews`);
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.message || "Reviews not loaded | Unexpected error");
        }
        const data = await response.json();
        setReviews(data);
        setFilteredReviews(data);
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Could not load reviews"
        );
      } finally {
        setLoading(false);
      }
    };
    fetchReviews();
  }, [product.id]);

  // Filter and sort reviews
  useEffect(() => {
    let updatedReviews = [...reviews];
    if (filters.platform !== "all")
      updatedReviews = updatedReviews.filter(
        (review) => review.source === filters.platform
      );
    if (filters.sentiment !== "all")
      updatedReviews = updatedReviews.filter(
        (review) => review.sentiment === filters.sentiment
      );
    if (filters.rating !== "all")
      updatedReviews = updatedReviews.filter(
        (review) => review.rating === parseInt(filters.rating, 10)
      );

    if (sorting) {
      updatedReviews.sort((a, b) => {
        if (sorting.key === "rating" || sorting.key === "relevance_score") {
          return sorting.direction === "asc"
            ? a[sorting.key] - b[sorting.key]
            : b[sorting.key] - a[sorting.key];
        }
        if (sorting.key === "review_date") {
          return sorting.direction === "asc"
            ? new Date(a[sorting.key]).getTime() -
                new Date(b[sorting.key]).getTime()
            : new Date(b[sorting.key]).getTime() -
                new Date(a[sorting.key]).getTime();
        }
        return 0;
      });
    }
    setFilteredReviews(updatedReviews);
  }, [filters, sorting, reviews]);

  // Scraping and sentiment analysis functions
  const scrapeReviews = async (platform: string, id: string) => {
    setScraping(true);
    try {
      const response = await fetch(
        `/api/scrape_${platform.toLowerCase()}_reviews/${id}`,
        { method: "POST" }
      );
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Scraping failed");
      }
      toast.success(`Started scraping reviews from ${platform}`);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to start scraping"
      );
    } finally {
      setScraping(false);
    }
  };

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

  // Sorting handler
  const handleSorting = (key: string) => {
    setSorting((prev) => {
      const direction =
        prev?.key === key && prev.direction === "asc" ? "desc" : "asc";
      return { key, direction };
    });
  };

  return (
    <div className="mt-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {product.platforms.map((platform) => (
          <Card key={platform.platform} className="p-6">
            <h3 className="text-lg font-medium mb-4">
              {platform.platform} Reviews
            </h3>
            <div className="space-y-4">
              <Button
                onClick={() => scrapeReviews(platform.platform, platform.id)}
                disabled={scraping}
                className="w-full mb-2"
              >
                {scraping ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Scrape Reviews
              </Button>
              <Button
                onClick={() => analyzeSentiment(platform.platform)}
                disabled={analyzing}
                className="w-full"
              >
                {analyzing ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Analyze Reviews
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Filter Options */}
      <div className="flex space-x-4 mb-4">
        <Select
          onValueChange={(value) =>
            setFilters((prev) => ({ ...prev, platform: value }))
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Platform" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Platforms</SelectItem>
            {[...new Set(reviews.map((review) => review.source))].map(
              (source) => (
                <SelectItem key={source} value={source}>
                  {source}
                </SelectItem>
              )
            )}
          </SelectContent>
        </Select>

        <Select
          onValueChange={(value) =>
            setFilters((prev) => ({ ...prev, sentiment: value }))
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Sentiment" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sentiments</SelectItem>
            <SelectItem value="POSITIVE">Positive</SelectItem>
            <SelectItem value="NEUTRAL">Neutral</SelectItem>
            <SelectItem value="NEGATIVE">Negative</SelectItem>
          </SelectContent>
        </Select>

        <Select
          onValueChange={(value) =>
            setFilters((prev) => ({ ...prev, rating: value }))
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Rating" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Ratings</SelectItem>
            {[...new Set(reviews.map((review) => review.rating))].map(
              (rating) => (
                <SelectItem key={rating} value={rating.toString()}>
                  {rating}
                </SelectItem>
              )
            )}
          </SelectContent>
        </Select>
      </div>

      {/* Reviews Table */}
      {loading ? (
        <div className="text-center">Loading reviews...</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell onClick={() => handleSorting("author")}>
                Author
                {sorting?.key === "author" && (
                  <SortArrow direction={sorting.direction} />
                )}
              </TableCell>
              <TableCell onClick={() => handleSorting("rating")}>
                Rating
              </TableCell>
              {sorting?.key === "rating" && (
                <SortArrow direction={sorting.direction} />
              )}
              <TableCell onClick={() => handleSorting("sentiment")}>
                Sentiment
              </TableCell>
              {sorting?.key === "sentiment" && (
                <SortArrow direction={sorting.direction} />
              )}
              <TableCell onClick={() => handleSorting("source")}>
                Source
              </TableCell>
              {sorting?.key === "source" && (
                <SortArrow direction={sorting.direction} />
              )}
              <TableCell onClick={() => handleSorting("review_date")}>
                Date
              </TableCell>
              {sorting?.key === "review_date" && (
                <SortArrow direction={sorting.direction} />
              )}
              <TableCell>Review</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredReviews.map((review) => (
              <TableRow key={review.id}>
                <TableCell>{review.author || "Unknown"}</TableCell>
                <TableCell>{review.rating}</TableCell>
                <TableCell className="text-sm flex flex-col items-center justify-center">
                  <span
                    className={`
                  ${
                    review.sentiment === "POSITIVE"
                      ? "text-green-800 bg-green-100"
                      : review.sentiment === "NEUTRAL"
                      ? "text-gray-800 bg-gray-100"
                      : review.sentiment === "NEGATIVE"
                      ? "text-red-800 bg-red-100"
                      : "text-yellow-800 bg-yellow-100"
                  } rounded-full px-2 py-1
                `}
                  >
                    {review.sentiment}
                  </span>
                </TableCell>
                <TableCell className="text-sm">
                  <span className={`${review.source === 'AMAZON' ? "text-[#ff9900]" : "text-[#287ff0]"}`}>{review.source}</span></TableCell>
                <TableCell>
                  {new Date(review.review_date).toLocaleDateString()}
                </TableCell>
                <TableCell>{review.review_text}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
