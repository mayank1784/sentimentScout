import Image from "next/image";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Heart, Smile, Frown, Star} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

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

  interface SentimentSummaryProps {
    sentimentData: SentimentData;  // Expecting a prop of type SentimentData
  }

  const SentimentSummary: React.FC<SentimentSummaryProps> = ({ sentimentData }) => {

return(
<div className="grid grid-cols-1 gap-6 mt-6">
      <div className="space-y-6">
        {/* Average Rating */}
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4">Average Rating</h3>
          <div className="flex items-center space-x-4">
            <Progress
              value={sentimentData.average_rating * 20} // Convert 5-star rating scale to 100%
              max={100}
              className="w-full"
            />
            <span>{sentimentData.average_rating.toFixed(1)} / 5</span>
          </div>
        </Card>

        {/* Most Frequent Rating */}
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4">Most Frequent Rating</h3>
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="px-4 py-1">
              {sentimentData.most_rating} Stars
            </Badge>
            {Array.from({ length: Math.floor(sentimentData.most_rating) }, (_, index) => (
     <Star className="h-6 w-6 text-yellow-500" key={index} />
    ))}
            
          </div>
        </Card>

        {/* Review Summary */}
        <div className="grid grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-medium mb-4">Positive Reviews</h3>
            <div className="flex justify-between">
              <Badge variant="outline" className="px-4 py-1">
                {sentimentData.positive_reviews}
              </Badge>
              <Smile className="h-6 w-6 text-green-500" />
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-medium mb-4">Neutral Reviews</h3>
            <div className="flex justify-between">
              <Badge variant="outline" className="px-4 py-1">
                {sentimentData.neutral_reviews}
              </Badge>
              <Frown className="h-6 w-6 text-gray-500" />
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-medium mb-4">Negative Reviews</h3>
            <div className="flex justify-between">
              <Badge variant="outline" className="px-4 py-1">
                {sentimentData.negative_reviews}
              </Badge>
              <Heart className="h-6 w-6 text-red-500" />
            </div>
          </Card>
        </div>

         <Card className="p-6">
      <h3 className="text-lg font-medium mb-4">Word Frequencies</h3>
      <ScrollArea className="max-h-60">
        <div className="space-y-2">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={sentimentData.word_frequencies}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="word" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="frequency" fill="#4CAF50" barSize={30} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ScrollArea>
    </Card>
      </div>

      {/* Word Cloud */}
      <div className="col-span-1">
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4">Word Cloud</h3>
          <div className="w-full h-72 flex justify-center items-center relative overflow-hidden">
            <Image
              src={`data:image/png;base64,${sentimentData.word_cloud}`}
              alt="Word Cloud"
              fill
              className="rounded-lg"
            />
          </div>
        </Card>
      </div>
    </div>)
}
export default SentimentSummary