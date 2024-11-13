
"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { DashboardData, Product } from "@/lib/types";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { PendingTasks } from "@/components/dashboard/pending-tasks";
import { toast } from "sonner";
import { FailedTasks } from "@/components/dashboard/recent-failed-task";
import ProductCard from "@/components/dashboard/product-card"
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const COLORS = ["#6FCF97", "#FF9AA2", "#2D9CDB"];

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [prods, setProds] = useState<{
    positive_prod: Product | null;
    negative_prod: Product | null;
    neutral_prod: Product | null;
  }>({
    positive_prod: null,
    negative_prod: null,
    neutral_prod: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch("/api/dashboard");
        if (!response.ok) throw new Error("Failed to fetch dashboard data");
        const dashboardData = await response.json();
        setData(dashboardData);
      } catch (error) {
        toast.error("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  useEffect(() => {
    const fetchProd = async (data: DashboardData) => {
      try {
        const { product_with_most_positive_reviews: pos, product_with_most_negative_reviews: neg, product_with_most_neutral_reviews: neu } = data;

        // Fetch products concurrently
        const [positiveProd, negativeProd, neutralProd] = await Promise.all([
          fetch(`/api/product/${pos}`).then(async (res) => {
            if (!res.ok) {
              const errorData = await res.json();
              throw new Error(errorData.message || "Positive product fetch failed");
            }
            return res.json();
          }),
          fetch(`/api/product/${neg}`).then(async (res) => {
            if (!res.ok) {
              const errorData = await res.json();
              throw new Error(errorData.message || "Negative product fetch failed");
            }
            return res.json();
          }),
          fetch(`/api/product/${neu}`).then(async (res) => {
            if (!res.ok) {
              const errorData = await res.json();
              throw new Error(errorData.message || "Neutral product fetch failed");
            }
            return res.json();
          })
        ]);

        setProds({
          positive_prod: positiveProd,
          negative_prod: negativeProd,
          neutral_prod: neutralProd,
        });
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to load product data");
      }
    };

    if (data && !prods.positive_prod && !prods.negative_prod && !prods.neutral_prod) {
      fetchProd(data);
    }
  }, [data, prods]);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!data) {
    return <div className="flex items-center justify-center min-h-screen">No data available</div>;
  }
  const reviewData = [
    { name: "Positive", value: data.total_positive_reviews },
    { name: "Negative", value: data.total_negative_reviews },
    { name: "Neutral", value: data.total_neutral_reviews },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <DashboardHeader />
      <DashboardStats data={data} />
      <PendingTasks tasks={data.pending_scraping_task_details} />
      <FailedTasks />
      
      {/* Displaying the products */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
       {/* Pie Chart */}
       <Card className="p-6 flex items-start justify-center">
        <div>
          <PieChart width={300} height={300}>
            <Pie
              data={reviewData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              label
            >
              {reviewData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
          </div>
        </Card>
      <div className="grid grid-cols-1 gap-4">
      {prods.positive_prod &&(<ProductCard product={prods.positive_prod} type={"positive"}/>)}
      {prods.negative_prod &&(<ProductCard product={prods.negative_prod} type={"negative"}/>)}
      {prods.neutral_prod &&(<ProductCard product={prods.neutral_prod} type={"neutral"}/>)}
      </div>
      </div>
    </div>
  );
}
