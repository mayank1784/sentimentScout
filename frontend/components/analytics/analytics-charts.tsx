import { Card } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

interface AnalyticsChartsProps {
  data: {
    sentiment_over_time: Array<{
      date: string;
      positive: number;
      negative: number;
      neutral: number;
    }>;
    platform_distribution: Array<{
      platform: string;
      reviews: number;
    }>;
  };
}

export function AnalyticsCharts({ data }: AnalyticsChartsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card className="p-6">
        <h3 className="text-lg font-medium mb-4">Sentiment Over Time</h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.sentiment_over_time}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="positive"
                stroke="hsl(var(--chart-1))"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="negative"
                stroke="hsl(var(--chart-2))"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="neutral"
                stroke="hsl(var(--chart-3))"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-medium mb-4">Reviews by Platform</h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.platform_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="platform" />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="reviews"
                fill="hsl(var(--chart-4))"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}