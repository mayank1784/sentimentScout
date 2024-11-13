
import { SideNav } from "@/components/dashboard/side-nav";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar (SideNav) will take full height */}
      <SideNav />

      {/* Main content area */}
      <main className="flex-1 overflow-auto max-h-screen">
        {children}
      </main>
    </div>
  );
}
