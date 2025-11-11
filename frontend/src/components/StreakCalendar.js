import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

export function StreakCalendar({ streakCount = 0, totalMessages = 0, lastEmailSent }) {
  const [calendarData, setCalendarData] = useState([]);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  useEffect(() => {
    generateCalendarData();
  }, [streakCount, totalMessages, lastEmailSent, currentMonth]);

  const generateCalendarData = () => {
    const data = [];
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    // Get first day of month and total days in month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDayOfWeek = firstDay.getDay(); // 0 = Sunday
    
    // Calculate total weeks needed
    const totalCells = Math.ceil((daysInMonth + startDayOfWeek) / 7) * 7;
    const weeks = totalCells / 7;
    
    const today = new Date();
    
    for (let week = 0; week < weeks; week++) {
      const weekData = [];
      for (let day = 0; day < 7; day++) {
        const cellIndex = week * 7 + day;
        const dayNum = cellIndex - startDayOfWeek + 1;
        
        if (dayNum < 1 || dayNum > daysInMonth) {
          // Empty cell
          weekData.push({
            date: null,
            level: -1,
            dayOfWeek: day,
            isToday: false,
            isEmpty: true
          });
        } else {
          const date = new Date(year, month, dayNum);
          
          // Determine if this day had activity
          let level = 0;
          if (lastEmailSent) {
            const lastSent = new Date(lastEmailSent);
            const daysSince = Math.floor((today - date) / (1000 * 60 * 60 * 24));
            
            // If within streak count and not in future, mark as active
            if (daysSince <= streakCount && daysSince >= 0 && date <= today) {
              level = 4; // High activity
            }
          }
          
          weekData.push({
            date: date.toISOString().split('T')[0],
            level,
            dayOfWeek: day,
            isToday: date.toDateString() === today.toDateString(),
            isEmpty: false,
            dayNum
          });
        }
      }
      data.push(weekData);
    }
    
    setCalendarData(data);
  };

  const getLevelColor = (level) => {
    if (level === -1) return "bg-transparent"; // Empty cells
    if (level === 0) return "bg-gray-100";
    if (level === 1) return "bg-green-200";
    if (level === 2) return "bg-green-300";
    if (level === 3) return "bg-green-400";
    return "bg-green-500";
  };

  const getDayLabel = (dayIndex) => {
    const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    return days[dayIndex];
  };

  const goToPreviousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    const today = new Date();
    const nextMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);
    // Don't go beyond current month
    if (nextMonth <= today) {
      setCurrentMonth(nextMonth);
    }
  };

  const goToCurrentMonth = () => {
    setCurrentMonth(new Date());
  };

  const isCurrentMonth = () => {
    const today = new Date();
    return currentMonth.getMonth() === today.getMonth() && 
           currentMonth.getFullYear() === today.getFullYear();
  };

  const getMonthYear = () => {
    return currentMonth.toLocaleString('default', { month: 'long', year: 'numeric' });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl md:text-3xl font-bold">
            Your Motivation Streak
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={goToPreviousMonth}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            {!isCurrentMonth() && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={goToCurrentMonth}
              >
                Today
              </Button>
            )}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={goToNextMonth}
              disabled={isCurrentMonth()}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Month and Year */}
        <div className="text-center mb-6">
          <h3 className="text-xl font-semibold">{getMonthYear()}</h3>
          <p className="text-sm text-muted-foreground mt-1">
            {totalMessages} total messages received
          </p>
        </div>

        {/* Calendar Grid */}
        <div className="space-y-3">
          {/* Day labels */}
          <div className="grid grid-cols-7 gap-2 text-center text-xs font-medium text-muted-foreground">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day}>{day}</div>
            ))}
          </div>

          {/* Weeks */}
          <div className="space-y-2">
            {calendarData.map((week, weekIndex) => (
              <div key={weekIndex} className="grid grid-cols-7 gap-2">
                {week.map((day, dayIndex) => (
                  <div
                    key={dayIndex}
                    className="aspect-square flex items-center justify-center"
                  >
                    {!day.isEmpty ? (
                      <div
                        className={`w-full h-full rounded-md flex items-center justify-center text-xs font-medium ${getLevelColor(day.level)} ${
                          day.isToday ? 'ring-2 ring-blue-500 ring-offset-1' : ''
                        } ${day.level > 0 ? 'text-white' : 'text-gray-600'} transition-all hover:scale-110 cursor-pointer`}
                        title={`${day.date}${day.level > 0 ? ' - Message received' : ' - No activity'}`}
                      >
                        {day.dayNum}
                      </div>
                    ) : (
                      <div className="w-full h-full"></div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground pt-4">
            <span>Less</span>
            {[0, 1, 2, 3, 4].map((level) => (
              <div
                key={level}
                className={`w-4 h-4 rounded ${getLevelColor(level)}`}
              />
            ))}
            <span>More</span>
          </div>
        </div>

        {/* Motivation message */}
        {streakCount > 0 && isCurrentMonth() && (
          <div className="mt-6 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg text-center">
            <p className="text-lg font-bold text-orange-600 mb-1">
              🔥 {streakCount} Day Streak!
            </p>
            <p className="text-sm text-gray-600">
              {streakCount >= 30 && "Amazing! You're on fire! Keep going!"}
              {streakCount >= 14 && streakCount < 30 && "Great job! Two weeks strong!"}
              {streakCount >= 7 && streakCount < 14 && "One week down! Keep it up!"}
              {streakCount > 0 && streakCount < 7 && "Great start! Keep the momentum going!"}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
