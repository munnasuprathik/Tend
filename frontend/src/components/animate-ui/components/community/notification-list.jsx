'use client';

import * as React from 'react';
import { Bell, X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { LiquidButton as Button } from '@/components/animate-ui/components/buttons/liquid';

const notificationTypes = {
  success: { icon: CheckCircle2, color: 'text-foreground bg-muted' },
  error: { icon: AlertCircle, color: 'text-foreground bg-muted' },
  info: { icon: Info, color: 'text-foreground bg-muted' },
  warning: { icon: AlertTriangle, color: 'text-foreground bg-muted' },
};

export function NotificationList({ className, showTrigger = true }) {
  const [notifications, setNotifications] = React.useState([]);
  const [isOpen, setIsOpen] = React.useState(false);

  // Listen for custom notification events
  React.useEffect(() => {
    const handleNotification = (event) => {
      const { type = 'info', message, title, duration = 5000 } = event.detail;
      addNotification({ type, message, title, duration });
    };

    window.addEventListener('show-notification', handleNotification);
    return () => window.removeEventListener('show-notification', handleNotification);
  }, []);

  const addNotification = ({ type, message, title, duration }) => {
    const id = Date.now() + Math.random();
    const notification = { id, type, message, title, duration };
    
    setNotifications((prev) => [...prev, notification]);

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  };

  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const unreadCount = notifications.length;

  return (
    <>
      {showTrigger && (
        <div className={cn(className || "fixed top-3 right-3 sm:top-4 sm:right-4 z-[100]")}>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(!isOpen)}
            className="relative shadow-sm hover:bg-background/80 bg-background/50 backdrop-blur-sm border border-border/40 h-9 w-9 sm:h-10 sm:w-10"
          >
            <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500" />
            )}
          </Button>
        </div>
      )}

      {isOpen && (
        <div className="fixed top-16 right-4 z-[100] w-96 max-w-[calc(100vw-2rem)]">
          <div className="bg-card border border-border rounded-lg shadow-xl p-4 max-h-[600px] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Notifications</h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
              >
                <X />
              </Button>
            </div>

            {notifications.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Bell className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="space-y-2">
                {notifications.map((notification) => {
                  const { icon: Icon, color } = notificationTypes[notification.type] || notificationTypes.info;
                  return (
                    <div
                      key={notification.id}
                      className={cn(
                        'flex items-start gap-3 p-3 rounded-lg border border-border bg-card',
                        'hover:bg-accent transition-colors'
                      )}
                    >
                      <div className={cn('p-2 rounded-full', color)}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        {notification.title && (
                          <p className="font-medium text-sm mb-1">{notification.title}</p>
                        )}
                        <p className="text-sm text-muted-foreground">{notification.message}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeNotification(notification.id)}
                        className="h-6 w-6 flex-shrink-0"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}

            {notifications.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setNotifications([])}
                  className="w-full"
                >
                  Clear All
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// Helper function to show notifications from anywhere in the app
export const showNotification = ({ type = 'info', message, title, duration = 5000 }) => {
  window.dispatchEvent(
    new CustomEvent('show-notification', {
      detail: { type, message, title, duration },
    })
  );
};

