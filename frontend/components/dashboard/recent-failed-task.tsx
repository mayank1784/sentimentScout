import { Card } from "@/components/ui/card";

import { formatDistanceToNow, subDays, parse } from "date-fns";
import { useEffect, useState } from "react";
import Link from "next/link"; // Assuming you're using Next.js for routing
import { toast } from "sonner"; // Assuming sonner is used for notifications


interface Task {
  id: string;
  fsn_asin: string;
  platform: string;
  status: string;
  created_at: string;
  message: string | null;
  product_id: string;
}

export function FailedTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const dateFormat = "yyyy-MM-dd HH:mm:ss";
  // Function to fetch tasks from the API and store them in localStorage
  const fetchTasks = async () => {
    try {
      const response = await fetch("/api/user_tasks?status=FAILED");
      if (!response.ok) throw new Error("Failed to fetch tasks");
      const data: Task[] = await response.json();

      // Filter tasks within the last 24 hours
      const recentTasks = data.filter((task) => {
        const taskDate = parse(task.created_at, dateFormat, new Date());
        return taskDate > subDays(new Date(), 1);
      });

      // Save the tasks to localStorage
      localStorage.setItem("failed_tasks", JSON.stringify(recentTasks));

      setTasks(recentTasks);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Error loading tasks");
    }
  };

  // Load tasks from localStorage if available
  useEffect(() => {
    const storedTasks = localStorage.getItem("failed_tasks");

    if (storedTasks) {
      setTasks(JSON.parse(storedTasks)); // Set tasks from localStorage
    } else {
      fetchTasks(); // Fetch tasks if not in localStorage
    }
  }, []);

  // Function to remove task from localStorage and the state
  const handleTaskClick = (taskId: string) => {
    setTasks((prevTasks) => {
      const updatedTasks = prevTasks.filter((task) => task.id !== taskId);
      localStorage.setItem("failed_tasks", JSON.stringify(updatedTasks)); // Update localStorage
      return updatedTasks;
    });
  };


  if (tasks.length === 0) {
    return null; // Return nothing if there are no tasks to display
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Recent Failed Tasks</h2>
      <div className="space-y-4">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
          >
            <div>
              <p className="font-medium">
                {task.platform} Scraping - Product ID: {task.fsn_asin}
              </p>
              <p className="text-sm text-gray-600">{task.message}</p>
              <p className="text-xs text-gray-500">
                Started {formatDistanceToNow(parse(task.created_at, dateFormat, new Date()))} ago
              </p>
            </div>
            <span className="px-3 py-1 text-sm font-medium text-white bg-red-500 rounded-full">
              {task.status}
            </span>
            {/* Link to the product page */}
            <Link href={`/products/${task.product_id}`} passHref  onClick={() => handleTaskClick(task.id)}
                className="ml-4 text-blue-500 hover:underline text-sm">
              
                View Product
            
            </Link>
          </div>
        ))}
      </div>
    </Card>
  );
}
