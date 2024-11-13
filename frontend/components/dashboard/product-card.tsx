"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import Image from "next/image";
import type { Product } from "@/lib/types";
import Link from "next/link";

interface ProductCardProps {
  product: Product;
  type: "positive" | "negative" | "neutral"
}

const ProductCard: React.FC<ProductCardProps> = ({ product, type }) => {

  return (
    <Card className="p-6 shadow-lg rounded-lg flex flex-col justify-between">
        <div className="flex flex-row w-full h-auto text-sm justify-end items-start text-white"><span className="bg-black p-2 rounded-lg">Most {type} Reviews</span></div>
      <div className="flex flex-col items-center">
        {product.image && (
          <div className="relative w-48 h-48">
            <Image
              src={product.image}
              alt={product.name}
              fill
              className="rounded-lg"
            />
          </div>
        )}

        <h2 className="text-lg font-semibold mt-4 text-center">
          {product.name}
        </h2>
        <p className="text-gray-600 text-sm mt-2 text-center">
          {product.description}
        </p>
        <div className="mt-4">
            <Link href={`/products/${product.id}?tab=analytics`}>
          <Button
            variant="outline"
         
            className="w-full text-center"
          >
            Go to Sentiment Analysis
          </Button> </Link>
        </div>
      </div>
      <div className="mt-4 flex justify-between text-sm text-gray-500">
        <div>
          <span className="font-medium">Platform:</span>{" "}
          {product.platforms.map((platform, index) => (
            <span key={platform.id}>
              {platform.platform}
              {index < product.platforms.length - 1 && ", "}
            </span>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default ProductCard;
