import React, { useState } from "react";
import { 
  BarChart3, 
  TrendingUp, 
  Trophy, 
  History, 
  Settings,
  Menu,
  X,
  User,
  LogOut,
  Mail,
  Sparkles,
  Flame
} from "lucide-react";
import { LiquidButton as Button } from "@/components/animate-ui/components/buttons/liquid";
import { cn } from "@/lib/utils";

/**
 * Dashboard Layout Component
 * Based on shadcn dashboard-01 design pattern
 * Integrates existing components while maintaining their order
 */
export function DashboardLayout({ 
  user, 
  onLogout, 
  activeTab = "overview",
  onTabChange,
  children 
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: "Overview", value: "overview", icon: BarChart3 },
    { name: "Analytics", value: "analytics", icon: TrendingUp },
    { name: "Achievements", value: "achievements", icon: Trophy },
    { name: "History", value: "history", icon: History },
    { name: "Settings", value: "settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar - Desktop (Minimal, just logo and user) */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-20 lg:flex-col">
        <div className="flex grow flex-col gap-y-6 overflow-y-auto border-r border-border/40 bg-background/50 backdrop-blur-sm px-3 pb-6">
          <div className="flex h-16 shrink-0 items-center justify-center pt-5">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
          </div>
          <div className="mt-auto pt-4 border-t border-border/40">
            <div className="flex flex-col items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-muted/50 flex items-center justify-center flex-shrink-0 border border-border/30">
                <User className="h-5 w-5 text-muted-foreground" />
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={onLogout}
                className="h-10 w-10 text-muted-foreground hover:text-foreground"
                data-testid="logout-btn"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" />
        </div>
      )}

      {/* Mobile sidebar - Simplified */}
      <aside
        className={cn(
          "fixed inset-y-0 z-50 lg:hidden",
          "w-64 bg-background/95 backdrop-blur-md border-r border-border/40",
          "transform transition-transform duration-300 ease-in-out",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex grow flex-col gap-y-6 overflow-y-auto px-5 pb-4">
          <div className="flex h-16 shrink-0 items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sparkles className="h-4.5 w-4.5 text-primary" />
              </div>
              <span className="text-lg font-semibold text-foreground">Tend</span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
              className="h-9 w-9"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <div className="mt-auto pt-4 border-t border-border/40">
            <div className="flex items-center gap-x-3 px-2 py-3 mb-3">
              <div className="h-9 w-9 rounded-lg bg-muted/50 flex items-center justify-center flex-shrink-0 border border-border/30">
                <User className="h-4.5 w-4.5 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">{user?.name || "User"}</p>
                <p className="text-xs text-muted-foreground truncate font-normal">{user?.email || ""}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              onClick={onLogout}
              className="w-full justify-start text-muted-foreground hover:text-foreground"
              data-testid="logout-btn"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-20">
        {/* Top header with navigation - Mobile & Desktop */}
        <div className="sticky top-0 z-40 border-b border-border/40 bg-background/95 backdrop-blur-md">
          {/* Mobile header */}
          <div className="flex h-16 shrink-0 items-center gap-x-4 px-4 sm:gap-x-6 sm:px-6 lg:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(true)}
              className="h-9 w-9"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2.5 flex-1">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sparkles className="h-4.5 w-4.5 text-primary" />
              </div>
              <span className="text-lg font-semibold text-foreground tracking-tight">Tend</span>
            </div>
          </div>

          {/* Unified Tab Navigation - Clean Slider */}
          <div className="px-4 sm:px-6 lg:px-10 py-2.5 border-t border-border/30 bg-background/95">
            <div className="mx-auto max-w-7xl">
              <div className="flex items-center gap-1 overflow-x-auto scrollbar-hide">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.value;
                  return (
                    <button
                      key={item.value}
                      onClick={() => onTabChange && onTabChange(item.value)}
                      className={cn(
                        "flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200 flex-shrink-0 relative",
                        isActive
                          ? "bg-primary text-primary-foreground shadow-sm"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                      )}
                    >
                      <Icon className={cn("h-4 w-4 shrink-0", isActive ? "text-primary-foreground" : "")} />
                      <span>{item.name}</span>
                      {isActive && (
                        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full bg-primary-foreground/50" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Main content area */}
        <main className="py-6 sm:py-8 px-4 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-7xl">
            {/* Content */}
            <div className="space-y-6 sm:space-y-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

