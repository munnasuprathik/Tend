import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"

const liquidButtonVariants = cva(
  "relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 overflow-hidden group touch-manipulation min-h-[44px] sm:min-h-0 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg]:flex-shrink-0 [&_svg]:h-4 [&_svg]:w-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90 active:bg-primary/80 before:absolute before:inset-0 before:bg-white/20 before:translate-x-[-100%] hover:before:translate-x-[100%] before:transition-transform before:duration-700",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 active:bg-destructive/80 before:absolute before:inset-0 before:bg-white/20 before:translate-x-[-100%] hover:before:translate-x-[100%] before:transition-transform before:duration-700",
        outline:
          "border border-input shadow-sm bg-background hover:bg-accent hover:text-accent-foreground active:bg-accent/80 before:absolute before:inset-0 before:bg-primary/10 before:translate-x-[-100%] hover:before:translate-x-[100%] before:transition-transform before:duration-700",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 active:bg-secondary/70 before:absolute before:inset-0 before:bg-white/20 before:translate-x-[-100%] hover:before:translate-x-[100%] before:transition-transform before:duration-700",
        ghost: "hover:bg-accent hover:text-accent-foreground active:bg-accent/80 before:absolute before:inset-0 before:bg-primary/10 before:translate-x-[-100%] hover:before:translate-x-[100%] before:transition-transform before:duration-700",
        link: "text-primary underline-offset-4 hover:underline active:text-primary/80",
      },
      size: {
        default: "h-9 sm:h-9 px-4 py-2 min-h-[44px] sm:min-h-[36px] [&_svg]:h-4 [&_svg]:w-4",
        sm: "h-8 sm:h-8 rounded-md px-3 text-xs min-h-[44px] sm:min-h-[32px] [&_svg]:h-3.5 [&_svg]:w-3.5",
        lg: "h-10 sm:h-10 rounded-md px-8 min-h-[44px] sm:min-h-[40px] [&_svg]:h-5 [&_svg]:w-5",
        icon: "h-9 w-9 sm:h-9 sm:w-9 min-h-[44px] min-w-[44px] sm:min-h-[36px] sm:min-w-[36px] [&_svg]:h-4 [&_svg]:w-4",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const LiquidButton = React.forwardRef(({ className, variant, size, asChild = false, children, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  
  return (
    <Comp
      className={cn(liquidButtonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </Comp>
  )
})
LiquidButton.displayName = "LiquidButton"

export { LiquidButton, liquidButtonVariants }

