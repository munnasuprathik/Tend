import React, { useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Target, Trophy, Flame, Calendar, TrendingUp } from "lucide-react";

const MILESTONE_DATES = [7, 14, 30, 50, 100, 200, 365];

export const StreakMilestones = React.memo(function StreakMilestones({ streakCount, lastEmailSent }) {
  const milestones = useMemo(() => {
    const currentStreak = streakCount || 0;
    const upcoming = MILESTONE_DATES.filter(m => m > currentStreak);
    const achieved = MILESTONE_DATES.filter(m => m <= currentStreak);
    
    // Calculate next milestone
    const nextMilestone = upcoming.length > 0 ? upcoming[0] : null;
    const daysUntilNext = nextMilestone ? nextMilestone - currentStreak : null;
    
    // Calculate estimated date for next milestone
    let estimatedDate = null;
    if (nextMilestone && lastEmailSent) {
      const lastDate = new Date(lastEmailSent);
      const daysToAdd = daysUntilNext;
      estimatedDate = new Date(lastDate);
      estimatedDate.setDate(estimatedDate.getDate() + daysToAdd);
    }
    
    return {
      currentStreak,
      nextMilestone,
      daysUntilNext,
      estimatedDate,
      upcoming: upcoming.slice(0, 5), // Show next 5 milestones
      achieved: achieved.slice(-3), // Show last 3 achieved
      allAchieved: achieved.length === MILESTONE_DATES.length
    };
  }, [streakCount, lastEmailSent]);

  const getMilestoneIcon = (days) => {
    if (days >= 365) return <Trophy className="h-5 w-5 text-yellow-500" />;
    if (days >= 100) return <Flame className="h-5 w-5 text-primary" />;
    if (days >= 30) return <Target className="h-5 w-5 text-blue-500" />;
    return <Calendar className="h-5 w-5 text-green-500" />;
  };

  const getMilestoneLabel = (days) => {
    if (days >= 365) return 'Legend';
    if (days >= 200) return 'Master';
    if (days >= 100) return 'Champion';
    if (days >= 50) return 'Warrior';
    if (days >= 30) return 'Veteran';
    if (days >= 14) return 'Dedicated';
    return 'Starter';
  };

  return (
    <div className="space-y-4">
      {/* Current Streak & Next Milestone */}
      <Card className="border border-border/30 hover:border-border/50 transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            Streak Milestones
          </CardTitle>
          <CardDescription>
            Track your progress and upcoming achievements
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Next Milestone */}
          {milestones.nextMilestone && (
            <div className="p-4 bg-primary/5 rounded-xl border border-primary/10 hover:border-primary/20 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-background border border-border/50">
                    {getMilestoneIcon(milestones.nextMilestone)}
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">
                      {milestones.nextMilestone} Day Milestone
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {getMilestoneLabel(milestones.nextMilestone)} Achievement
                    </p>
                  </div>
                </div>
                <Badge variant="outline" className="bg-background/50 backdrop-blur-sm border-primary/20 text-primary">
                  {milestones.daysUntilNext} days to go
                </Badge>
              </div>
              {milestones.estimatedDate && (
                <p className="text-xs text-muted-foreground mt-3 pl-14 border-l-2 border-primary/20 pl-3 ml-1">
                  Estimated date: {milestones.estimatedDate.toLocaleDateString()}
                </p>
              )}
            </div>
          )}

          {milestones.allAchieved && (
            <div className="p-6 bg-yellow-500/5 rounded-xl border border-yellow-500/20 text-center">
              <div className="w-12 h-12 mx-auto bg-yellow-500/10 rounded-full flex items-center justify-center mb-3">
                <Trophy className="h-6 w-6 text-yellow-600" />
              </div>
              <p className="font-semibold text-yellow-700">Congratulations!</p>
              <p className="text-sm text-yellow-600/80">You've achieved all milestones!</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Achieved Milestones */}
      {milestones.achieved.length > 0 && (
        <Card className="border border-border/30 hover:border-border/50 transition-all duration-300">
          <CardHeader>
            <CardTitle className="text-lg">Recently Achieved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {milestones.achieved.map((days) => (
                <div
                  key={days}
                  className="flex items-center justify-between p-3 bg-green-500/5 rounded-xl border border-green-500/10 hover:border-green-500/20 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-background border border-border/50">
                      {getMilestoneIcon(days)}
                    </div>
                    <div>
                      <p className="font-semibold text-foreground">{days} Day Milestone</p>
                      <p className="text-xs text-muted-foreground">{getMilestoneLabel(days)}</p>
                    </div>
                  </div>
                  <Badge className="bg-green-600 text-white border-0">Achieved</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upcoming Milestones */}
      {milestones.upcoming.length > 0 && (
        <Card className="border border-border/30 hover:border-border/50 transition-all duration-300 opacity-80 hover:opacity-100">
          <CardHeader>
            <CardTitle className="text-lg text-muted-foreground">Upcoming Milestones</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {milestones.upcoming.map((days) => {
                const daysToGo = days - milestones.currentStreak;
                return (
                  <div
                    key={days}
                    className="flex items-center justify-between p-3 bg-muted/30 rounded-xl border border-border/40"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-background/50 border border-border/30 grayscale opacity-50">
                        {getMilestoneIcon(days)}
                      </div>
                      <div>
                        <p className="font-medium text-muted-foreground">{days} Day Milestone</p>
                        <p className="text-xs text-muted-foreground/70">
                          {getMilestoneLabel(days)} • {daysToGo} days to go
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-muted-foreground bg-background/50">
                      Locked
                    </Badge>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
});

