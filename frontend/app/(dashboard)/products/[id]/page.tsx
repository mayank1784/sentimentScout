"use client";

import { useEffect, useState } from "react";
import { Product } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ProductAnalytics } from "@/components/products/product-analytics";
import { ProductReviews } from "@/components/products/product-reviews";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { useRouter, useSearchParams } from "next/navigation";

export default function ProductPage({ params }: { params: { id: string } }) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const searchParams = useSearchParams();  // Hook to read the URL query params
  
  const activeTab = searchParams.get('tab') || "reviews"; 

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await fetch(`/api/product/${params.id}`);
        if (!response.ok) throw new Error("Failed to fetch product");
        const data = await response.json();
        setProduct(data);
      } catch (error) {
        toast.error("Failed to load product");
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [params.id]);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this product?")) return;

    try {
      const response = await fetch(`/api/product/${params.id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete product");
      toast.success("Product deleted successfully");
      router.push("/products");
    } catch (error) {
      toast.error("Failed to delete product");
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!product) {
    return <div className="flex items-center justify-center min-h-screen">Product not found</div>;
  }

  const handleTabChange = (tab: string) => {
    router.push(`/products/${params.id}?tab=${tab}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
          <p className="text-gray-600">{product.description}</p>
        </div>
        <div className="space-x-4">
          <Button variant="outline" onClick={() => router.push(`/products/edit/${params.id}`)}>
            Edit Product
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            Delete Product
          </Button>
        </div>
      </div>

      <Tabs defaultValue={activeTab} onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="reviews">Reviews</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>
        <TabsContent value="reviews">
          <ProductReviews product={product} />
        </TabsContent>
        <TabsContent value="analytics">
          <ProductAnalytics product={product} />
        </TabsContent>
      </Tabs>
    </div>
  );
}