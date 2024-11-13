import { Product } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart3, ExternalLink, Trash2, PackagePlus } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

interface ProductListProps {
  products: Product[];
}

export function ProductList({ products }: ProductListProps) {
  const handleDelete = async (productId: number) => {
    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete product");
      toast.success("Product deleted successfully");
      // Refresh the page to update the list
      window.location.reload();
    } catch (error) {
      toast.error("Failed to delete product");
    }
  };

  if (products.length === 0) {
    return (
      <Card className="p-8 text-center">
        <h3 className="text-lg font-medium mb-2">No products found</h3>
        <p className="text-gray-600 mb-4">Start by adding your first product</p>
        <Link href="/products/new">
          <Button>
            <PackagePlus className="mr-2 h-4 w-4" />
            Add Product
          </Button>
        </Link>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {products.map((product) => (
        <Card key={product.id} className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-medium">{product.name}</h3>
              <p className="text-sm text-gray-600">{product.description}</p>
            </div>
            {product.image && (
              <img
                src={product.image}
                alt={product.name}
                className="w-16 h-16 object-cover rounded"
              />
            )}
          </div>

          <div className="space-y-2">
            {product.platforms.map((platform) => (
              <div
                key={platform.id}
                className="flex items-center text-sm text-gray-600"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                {platform.platform}: {platform.id}
              </div>
            ))}
          </div>

          <div className="flex justify-between mt-4 pt-4 border-t">
            <Link href={`/products/${product.id}`}>
              <Button variant="outline" size="sm">
                <BarChart3 className="w-4 h-4 mr-2" />
                View Analysis
              </Button>
            </Link>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => handleDelete(product.id)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
