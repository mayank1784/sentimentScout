
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
    <Card className="p-6 mb-5">
      <h2 className="text-xl font-bold mb-4">Pending Tasks</h2>
      <div className="space-y-4">
        {tasks.map((task) => {
          const parsedDate = new Date(task.created_at); // Use Date constructor to handle the string

          // Check if the date is valid before proceeding
          if (isNaN(parsedDate.getTime())) {
            return (
              <div
                key={task.task_id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium">
                    {task.platform} Scraping - Product ID: {task.product_id}
                  </p>
                  <p className="text-sm text-gray-600">{task.message}</p>
                  <p className="text-xs text-gray-500">Invalid Date Format</p>
                </div>
                <span className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-full">
                  {task.status}
                </span>
              </div>
            );
          }

          return (
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
                  Started {formatDistanceToNow(parsedDate)} ago
                </p>
              </div>
              <span className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-full">
                {task.status}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
