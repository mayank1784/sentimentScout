import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { BarChart3, LineChart, Package2, Star } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Sentiment Scout
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Analyze product reviews from Amazon and Flipkart with advanced sentiment analysis
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/login">
              <Button size="lg">Login</Button>
            </Link>
            <Link href="/register">
              <Button size="lg" variant="outline">Register</Button>
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <Card className="p-6">
            <Package2 className="w-12 h-12 mb-4 text-blue-500" />
            <h3 className="text-xl font-semibold mb-2">Product Management</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Easily manage and track your products across multiple platforms
            </p>
          </Card>
          <Card className="p-6">
            <Star className="w-12 h-12 mb-4 text-yellow-500" />
            <h3 className="text-xl font-semibold mb-2">Review Analysis</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Get detailed insights from customer reviews using AI
            </p>
          </Card>
          <Card className="p-6">
            <BarChart3 className="w-12 h-12 mb-4 text-green-500" />
            <h3 className="text-xl font-semibold mb-2">Sentiment Analysis</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Understand customer sentiment with advanced analytics
            </p>
          </Card>
          <Card className="p-6">
            <LineChart className="w-12 h-12 mb-4 text-purple-500" />
            <h3 className="text-xl font-semibold mb-2">Trend Tracking</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Track review trends and patterns over time
            </p>
          </Card>
        </div>

        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Start Analyzing Reviews Today</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-8">
            Get valuable insights from your product reviews across multiple platforms
          </p>
          <Link href="/register">
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </main>
  );
}