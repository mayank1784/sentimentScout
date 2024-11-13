import { Card } from "@/components/ui/card";
import { ThumbsUp, ThumbsDown, Minus, TrendingUp } from "lucide-react";

interface AnalyticsSummaryProps {
  data: {
    positive_percentage: number;
    negative_percentage: number;
    neutral_percentage: number;
    trend: "up" | "down" | "stable";
  };
}

export function AnalyticsSummary({ data }: AnalyticsSummaryProps) {
  const stats = [
    {
      title: "Positive Reviews",
      value: `${data.positive_percentage}%`,
      icon: ThumbsUp,
      color: "text-green-500",
    },
    {
      title: "Negative Reviews",
      value: `${data.negative_percentage}%`,
      icon: ThumbsDown,
      color: "text-red-500",
    },
    {
      title: "Neutral Reviews",
      value: `${data.neutral_percentage}%`,
      icon: Minus,
      color: "text-yellow-500",
    },
    {
      title: "Overall Trend",
      value: data.trend.charAt(0).toUpperCase() + data.trend.slice(1),
      icon: TrendingUp,
      color: "text-blue-500",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat) => (
        <Card key={stat.title} className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{stat.title}</p>
              <p className="text-3xl font-bold">{stat.value}</p>
            </div>
            <stat.icon className={`w-8 h-8 ${stat.color}`} />
          </div>
        </Card>
      ))}
    </div>
  );
}