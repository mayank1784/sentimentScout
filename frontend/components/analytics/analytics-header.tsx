import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

export function AnalyticsHeader() {
  const exportData = async () => {
    try {
      const response = await fetch("/api/analytics/export");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "analytics-report.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Failed to export data:", error);
    }
  };

  return (
    <div className="flex justify-between items-center mb-8">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-gray-600">Review analysis and insights</p>
      </div>
      <Button onClick={exportData}>
        <Download className="mr-2 h-4 w-4" />
        Export Report
      </Button>
    </div>
  );
}