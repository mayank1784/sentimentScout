import { Button } from "@/components/ui/button";
import { PackagePlus } from "lucide-react";
import Link from "next/link";

export function ProductHeader() {
  return (
    <div className="flex justify-between items-center mb-8">
      <div>
        <h1 className="text-3xl font-bold">Products</h1>
        <p className="text-gray-600">Manage your products and their reviews</p>
      </div>
      <Link href="/products/new">
        <Button>
          <PackagePlus className="mr-2 h-4 w-4" />
          Add Product
        </Button>
      </Link>
    </div>
  );
}
