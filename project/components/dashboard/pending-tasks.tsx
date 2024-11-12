import { Card } from "@/components/ui/card";
import { DashboardData } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";

interface PendingTasksProps {
  tasks: DashboardData["pending_scraping_task_details"];
}

export function PendingTasks({ tasks }: PendingTasksProps) {
  if (tasks.length === 0) {
    return null;
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Pending Tasks</h2>
      <div className="space-y-4">
        {tasks.map((task) => (
          <div
            key={task.task_id}
            className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
          >
            <div>
              <p className="font-medium">
                {task.platform} Scraping - Product ID: {task.product_id}
              </p>
              <p className="text-sm text-gray-600">{task.message}</p>
              <p className="text-xs text-gray-500">
                Started {formatDistanceToNow(new Date(task.created_at))} ago
              </p>
            </div>
            <span className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-full">
              {task.status}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}