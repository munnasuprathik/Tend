import * as React from "react";
import {
  addDays,
  addMonths,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isSameDay,
  isSameMonth,
  startOfMonth,
  startOfWeek,
  subMonths,
} from "date-fns";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";
import { liquidButtonVariants as buttonVariants } from "@/components/animate-ui/components/buttons/liquid";

const WEEKDAY_LABELS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

function Calendar({
  className,
  selected,
  onSelect,
  disableOutsideDays = false,
  minDate,
  maxDate,
}) {
  const initialMonth = React.useMemo(() => {
    if (selected instanceof Date) return selected;
    return new Date();
  }, [selected]);

  const [currentMonth, setCurrentMonth] = React.useState(startOfMonth(initialMonth));

  React.useEffect(() => {
    if (selected instanceof Date && !isSameMonth(selected, currentMonth)) {
      setCurrentMonth(startOfMonth(selected));
    }
  }, [selected, currentMonth]);

  const goToPreviousMonth = () => {
    const previous = startOfMonth(subMonths(currentMonth, 1));
    if (minDate && previous < startOfMonth(minDate)) return;
    setCurrentMonth(previous);
  };

  const goToNextMonth = () => {
    const next = startOfMonth(addMonths(currentMonth, 1));
    if (maxDate && next > startOfMonth(maxDate)) return;
    setCurrentMonth(next);
  };

  const weeks = React.useMemo(() => {
    const start = startOfWeek(startOfMonth(currentMonth));
    const end = endOfWeek(endOfMonth(currentMonth));
    const days = eachDayOfInterval({ start, end });

    const chunked = [];
    for (let i = 0; i < days.length; i += 7) {
      chunked.push(days.slice(i, i + 7));
    }
    return chunked;
  }, [currentMonth]);

  const isDayDisabled = (day) => {
    if (disableOutsideDays && !isSameMonth(day, currentMonth)) return true;
    if (minDate && day < startOfDay(minDate)) return true;
    if (maxDate && day > startOfDay(maxDate)) return true;
    return false;
  };

  return (
    <div className={cn("w-full max-w-sm p-4", className)}>
      <div className="flex items-center justify-between mb-4">
        <button
          type="button"
          onClick={goToPreviousMonth}
          className={cn(buttonVariants({ variant: "outline" }), "h-8 w-8 p-0")}
          aria-label="Previous month"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <div className="text-sm font-medium">
          {format(currentMonth, "MMMM yyyy")}
        </div>
        <button
          type="button"
          onClick={goToNextMonth}
          className={cn(buttonVariants({ variant: "outline" }), "h-8 w-8 p-0")}
          aria-label="Next month"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      <div className="grid grid-cols-7 gap-1 text-xs font-medium text-muted-foreground mb-1">
        {WEEKDAY_LABELS.map((day) => (
          <div key={day} className="text-center">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1 text-sm">
        {weeks.map((week, idx) => (
          <React.Fragment key={idx}>
            {week.map((day) => {
              const outsideMonth = !isSameMonth(day, currentMonth);
              const disabled = isDayDisabled(day);
              const isSelected = selected instanceof Date && isSameDay(day, selected);

              return (
                <button
                  key={day.toISOString()}
                  type="button"
                  disabled={disabled}
                  onClick={() => onSelect?.(day)}
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-8 w-full p-0 font-normal",
                    outsideMonth && "text-muted-foreground opacity-60",
                    disabled && "opacity-40 cursor-not-allowed",
                    isSelected && "bg-primary text-primary-foreground hover:bg-primary"
                  )}
                >
                  {format(day, "d")}
                </button>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

Calendar.displayName = "Calendar";

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export { Calendar };
