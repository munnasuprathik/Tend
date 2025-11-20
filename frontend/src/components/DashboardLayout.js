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
import { NotificationList } from "@/components/animate-ui/components/community/notification-list";
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
              <div className="h-10 w-10 rounded-xl bg-muted/50 flex items-center justify-center flex-shrink-0 border border-border/30 overflow-hidden">
                {user?.image_url ? (
                  <img 
                    src={user.image_url} 
                    alt={user.name || "User"} 
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <User className="h-5 w-5 text-muted-foreground" />
                )}
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
          "w-72 max-w-[85vw] bg-background/95 backdrop-blur-md border-r border-border/40",
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
              className="h-11 w-11 sm:h-9 sm:w-9 touch-manipulation"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <div className="mt-auto pt-4 border-t border-border/40">
            <div className="flex items-center gap-x-3 px-2 py-3 mb-3">
              <div className="h-9 w-9 rounded-lg bg-muted/50 flex items-center justify-center flex-shrink-0 border border-border/30 overflow-hidden">
                {user?.image_url ? (
                  <img 
                    src={user.image_url} 
                    alt={user.name || "User"} 
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <User className="h-4.5 w-4.5 text-muted-foreground" />
                )}
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
          {/* Mobile header - Instagram Style */}
          <div className="flex h-14 shrink-0 items-center justify-between px-4 lg:hidden bg-background border-b border-border/20">
            {/* Left: Logo (Instagram style text) */}
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-foreground tracking-tight font-sans">Tend</span>
              <div className="h-1.5 w-1.5 rounded-full bg-primary/80 mb-3" /> {/* Subtle accent dot */}
            </div>
            
            {/* Right: Actions */}
            <div className="flex items-center gap-1">
              {/* Notification Bell */}
              <NotificationList className="relative top-0 right-0 z-10" />
              
              {/* Logout Button (Replaces Menu/Slider) */}
              <Button
                variant="ghost"
                size="icon"
                onClick={onLogout}
                className="h-11 w-11 sm:h-9 sm:w-9 text-muted-foreground hover:text-destructive transition-colors hover:bg-muted/50 touch-manipulation"
              >
                <LogOut className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Unified Tab Navigation - Desktop Only */}
          <div className="hidden lg:block px-10 py-2.5 border-t border-border/30 bg-background/95">
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

        {/* Main content area - Adjusted for bottom nav on mobile */}
        <main className="py-4 sm:py-8 px-4 sm:px-6 lg:px-10 pb-20 sm:pb-24 lg:pb-8">
          <div className="mx-auto max-w-7xl">
            {/* Content */}
            <div className="space-y-6 sm:space-y-8">
              {children}
            </div>
          </div>
        </main>

        {/* Mobile Bottom Dock Navigation - Instagram Style Refined */}
        <div className="fixed bottom-0 inset-x-0 z-50 lg:hidden pb-safe-area-inset-bottom bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 border-t border-border/10 shadow-[0_-1px_3px_rgba(0,0,0,0.02)]">
          <div className="flex items-center justify-between h-18 px-4 sm:px-12 max-w-md mx-auto gap-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.value;
              
              // Special case for Settings/Profile - mimic Instagram profile tab
              if (item.value === "settings") {
                 return (
                   <button
                    key={item.value}
                    onClick={() => onTabChange && onTabChange(item.value)}
                    className="flex items-center justify-center w-12 h-12 sm:w-10 sm:h-10 rounded-full transition-transform active:scale-90 touch-manipulation"
                  >
                    <div className={cn(
                      "h-8 w-8 sm:h-7 sm:w-7 rounded-full overflow-hidden ring-offset-background transition-all duration-200",
                      isActive ? "ring-2 ring-primary ring-offset-2" : "ring-1 ring-border"
                    )}>
                      <div className="h-full w-full bg-muted flex items-center justify-center">
                         {user?.image_url ? (
                            <img src={user.image_url} alt="Profile" className="h-full w-full object-cover" />
                         ) : (
                            <User className="h-4 w-4 text-muted-foreground" />
                         )}
                      </div>
                    </div>
                  </button>
                 )
              }

              return (
                <button
                  key={item.value}
                  onClick={() => onTabChange && onTabChange(item.value)}
                  className="flex items-center justify-center w-12 h-12 sm:w-10 sm:h-10 rounded-lg active:scale-90 transition-transform hover:bg-muted/30 touch-manipulation"
                >
                  <div className="relative">
                    <Icon 
                      className={cn(
                        "h-[28px] w-[28px] sm:h-[26px] sm:w-[26px] transition-all duration-300", 
                        isActive 
                          ? "stroke-[2.5px] text-primary scale-105" 
                          : "stroke-[1.75px] text-muted-foreground hover:text-foreground"
                      )} 
                    />
                    
                    {/* Notification dot for Overview */}
                    {item.name === "Overview" && (
                       <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                         <span className="absolute inline-flex h-full w-full rounded-full bg-red-500 border-2 border-background"></span>
                       </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

