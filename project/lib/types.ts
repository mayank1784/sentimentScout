export type Product = {
  id: number;
  name: string;
  description: string;
  created_at: string;
  image?: string;
  platforms: {
    platform: string;
    id: string;
  }[];
};

export type DashboardData = {
  total_reviews: number;
  total_products: number;
  pending_scraping_tasks: number;
  pending_scraping_task_details: {
    task_id: string;
    status: string;
    created_at: string;
    message: string;
    platform: string;
    product_id: number;
  }[];
  total_positive_reviews: number;
  total_negative_reviews: number;
  total_neutral_reviews: number;
  average_rating: number;
  most_rating: number;
  product_with_most_positive_reviews: number;
  product_with_most_negative_reviews: number;
  product_with_most_neutral_reviews: number;
};