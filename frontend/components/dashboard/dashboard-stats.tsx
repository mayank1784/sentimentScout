import { Card } from "@/components/ui/card";
import { DashboardData } from "@/lib/types";
import { BarChart3, MessageSquare, Package2, Star } from "lucide-react";

interface DashboardStatsProps {
  data: DashboardData;
}

export function DashboardStats({ data }: DashboardStatsProps) {
  const stats = [
    {
      title: "Total Products",
      value: data.total_products,
      icon: Package2,
      color: "text-blue-500",
    },
    {
      title: "Total Reviews",
      value: data.total_reviews,
      icon: MessageSquare,
      color: "text-green-500",
    },
    {
      title: "Average Rating",
      value: data.average_rating.toFixed(1),
      icon: Star,
      color: "text-yellow-500",
    },
    {
      title: "Most Rating",
      value: data.most_rating.toFixed(1),
      icon: Star,
      color: "text-yellow-800"
    },
    {
      title: "Pending Tasks",
      value: data.pending_scraping_tasks,
      icon: BarChart3,
      color: "text-purple-500",
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