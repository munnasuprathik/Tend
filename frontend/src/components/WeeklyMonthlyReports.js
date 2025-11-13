import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Calendar, TrendingUp, Mail, Target, Award, Download, Loader2 } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { exportAnalytics } from "@/utils/exportData";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const WeeklyMonthlyReports = React.memo(function WeeklyMonthlyReports({ email, user, refreshKey }) {
  const [weeklyData, setWeeklyData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchWeeklyReport = async () => {
    try {
      const response = await axios.get(`${API}/users/${email}/analytics/weekly?weeks=4`);
      setWeeklyData(response.data);
    } catch (error) {
      console.error('Failed to fetch weekly report:', error);
      toast.error('Failed to load weekly report');
    }
  };

  const fetchMonthlyReport = async () => {
    try {
      const response = await axios.get(`${API}/users/${email}/analytics/monthly?months=6`);
      setMonthlyData(response.data);
    } catch (error) {
      console.error('Failed to fetch monthly report:', error);
      toast.error('Failed to load monthly report');
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await Promise.all([fetchWeeklyReport(), fetchMonthlyReport()]);
      setLoading(false);
    };
    fetchData();
  }, [email, refreshKey]);

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-indigo-600" />
              Weekly & Monthly Reports
            </CardTitle>
            <CardDescription>
              Activity summaries and insights
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const analytics = {
                longest_streak: user?.streak_count || 0,
                total_achievements: 0,
                unlocked_achievements: 0,
                best_day: weeklyData?.best_day || 'N/A',
                avg_messages_per_week: weeklyData?.avg_messages_per_week || 0
              };
              exportAnalytics(user, analytics);
            }}
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="weekly" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="weekly">Weekly Report</TabsTrigger>
            <TabsTrigger value="monthly">Monthly Report</TabsTrigger>
          </TabsList>

          <TabsContent value="weekly" className="space-y-4 mt-4">
            {weeklyData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Mail className="h-4 w-4 text-blue-600" />
                      <p className="text-sm text-muted-foreground">Total Messages</p>
                    </div>
                    <p className="text-2xl font-bold text-blue-600">{weeklyData.total_messages || 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">{weeklyData.period || 'Last 4 weeks'}</p>
                  </div>

                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <p className="text-sm text-muted-foreground">Avg Rating</p>
                    </div>
                    <p className="text-2xl font-bold text-green-600">
                      {weeklyData.avg_rating ? weeklyData.avg_rating.toFixed(1) : 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {weeklyData.total_feedback || 0} feedback{weeklyData.total_feedback !== 1 ? 's' : ''}
                    </p>
                  </div>

                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-4 w-4 text-purple-600" />
                      <p className="text-sm text-muted-foreground">Current Streak</p>
                    </div>
                    <p className="text-2xl font-bold text-purple-600">
                      {weeklyData.streak_count || 0}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">Days in a row</p>
                  </div>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg border">
                  <h4 className="font-semibold mb-2">Period Summary</h4>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Start: {weeklyData.start_date ? new Date(weeklyData.start_date).toLocaleDateString() : 'N/A'}</p>
                    <p>End: {weeklyData.end_date ? new Date(weeklyData.end_date).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">No weekly data available</p>
            )}
          </TabsContent>

          <TabsContent value="monthly" className="space-y-4 mt-4">
            {monthlyData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Mail className="h-4 w-4 text-blue-600" />
                      <p className="text-sm text-muted-foreground">Total Messages</p>
                    </div>
                    <p className="text-2xl font-bold text-blue-600">{monthlyData.total_messages || 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">{monthlyData.period || 'Last 6 months'}</p>
                  </div>

                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-4 w-4 text-purple-600" />
                      <p className="text-sm text-muted-foreground">Current Streak</p>
                    </div>
                    <p className="text-2xl font-bold text-purple-600">
                      {monthlyData.streak_count || 0}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">Days in a row</p>
                  </div>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg border">
                  <h4 className="font-semibold mb-2">Period Summary</h4>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Start: {monthlyData.start_date ? new Date(monthlyData.start_date).toLocaleDateString() : 'N/A'}</p>
                    <p>End: {monthlyData.end_date ? new Date(monthlyData.end_date).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">No monthly data available</p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
});

