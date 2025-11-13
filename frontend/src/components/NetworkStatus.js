import { useState, useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { WifiOff, Wifi } from "lucide-react";

export function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setWasOffline(true);
      // Clear the offline message after 3 seconds
      setTimeout(() => setWasOffline(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setWasOffline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline && !wasOffline) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      {!isOnline ? (
        <Alert variant="destructive" className="shadow-lg">
          <WifiOff className="h-4 w-4" />
          <AlertDescription>
            You're offline. Some features may not work.
          </AlertDescription>
        </Alert>
      ) : wasOffline ? (
        <Alert className="bg-green-50 border-green-200 shadow-lg">
          <Wifi className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Connection restored!
          </AlertDescription>
        </Alert>
      ) : null}
    </div>
  );
}

