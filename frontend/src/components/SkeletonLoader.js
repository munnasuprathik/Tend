import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function SkeletonLoader({ variant = "default", count = 1 }) {
  const skeletons = Array.from({ length: count });

  if (variant === "message") {
    return (
      <>
        {skeletons.map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </>
    );
  }

  if (variant === "card") {
    return (
      <>
        {skeletons.map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-5 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            </CardContent>
          </Card>
        ))}
      </>
    );
  }

  if (variant === "calendar") {
    return (
      <Card className="animate-pulse">
        <CardContent className="p-6">
          <div className="h-6 bg-gray-200 rounded w-1/3 mx-auto mb-6"></div>
          <div className="flex flex-wrap gap-2 justify-center">
            {Array.from({ length: 30 }).map((_, i) => (
              <div key={i} className="w-10 h-10 bg-gray-200 rounded-md"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Default skeleton
  return (
    <>
      {skeletons.map((_, i) => (
        <div key={i} className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      ))}
    </>
  );
}

