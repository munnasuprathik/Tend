import * as React from "react"

import { cn } from "@/lib/utils"

const Textarea = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex w-full rounded-lg border border-input/60 bg-background px-3 py-2 text-base shadow-sm transition-all duration-200 placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/20 focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm min-h-[44px] sm:min-h-[60px] touch-manipulation hover:border-input",
        className
      )}
      ref={ref}
      {...props} />
  );
})
Textarea.displayName = "Textarea"

export { Textarea }
