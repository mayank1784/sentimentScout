"use client"
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  BarChart3,
  Home,
  LogOut,
  Package2,
  Settings,
} from "lucide-react";

const links = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Products", href: "/products", icon: Package2 },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function SideNav() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen flex-col justify-between border-r bg-white w-64">
      <div className="px-4 py-6">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 font-semibold text-xl mb-8"
        >
          <BarChart3 className="h-6 w-6" />
          <span>Review Analyzer</span>
        </Link>
        <nav className="space-y-2">
          {links.map((link) => {
            const LinkIcon = link.icon;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 text-gray-600 rounded-lg hover:bg-gray-100",
                  pathname === link.href ? "bg-gray-100 text-gray-900" : ""
                )}
              >
                <LinkIcon className="w-5 h-5" />
                {link.name}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="border-t p-4">
        <button className="flex items-center gap-2 px-3 py-2 text-gray-600 rounded-lg hover:bg-gray-100 w-full">
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>
    </div>
  );
}