"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { AnalyticsHeader } from "@/components/analytics/analytics-header";
import { AnalyticsCharts } from "@/components/analytics/analytics-charts";
import { AnalyticsSummary } from "@/components/analytics/analytics-summary";
import { toast } from "sonner";

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch("/api/analytics");
        if (!response.ok) throw new Error("Failed to fetch analytics");
        const analyticsData = await response.json();
        setData(analyticsData);
      } catch (error) {
        toast.error("Failed to load analytics data");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!data) {
    return <div className="flex items-center justify-center min-h-screen">No data available</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <AnalyticsHeader />
      <AnalyticsSummary data={data} />
      <AnalyticsCharts data={data} />
    </div>
  );
}