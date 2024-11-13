import { Button } from "@/components/ui/button";
import { PackagePlus } from "lucide-react";
import Link from "next/link";

export function DashboardHeader() {
  return (
    <div className="flex justify-between items-center mb-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600">
          Monitor your products and review analysis
        </p>
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
