import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LiquidButton as Button } from "@/components/animate-ui/components/buttons/liquid";
import { Badge } from "@/components/ui/badge";
import { X, Mail, Star, Activity, Clock, TrendingUp, User, Calendar, MessageSquare, Trophy, Award, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';
import { formatDateTimeForTimezone, getDisplayTimezone } from "@/utils/timezoneFormatting";

// Use centralized API configuration
import API_CONFIG from '@/config/api';
const API = API_CONFIG.API_BASE;

export function AdminUserDetails({ email, adminToken, onClose }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [userAchievements, setUserAchievements] = useState(null);
  const [allAchievements, setAllAchievements] = useState([]);

  useEffect(() => {
    if (email && adminToken) {
      fetchUserDetails();
    }
  }, [email, adminToken]);

  const fetchUserDetails = async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${adminToken}` };
      const [detailsRes, achievementsRes, allAchievementsRes] = await Promise.all([
        axios.get(`${API}/admin/users/${encodeURIComponent(email)}/details`, { headers }),
        axios.get(`${API}/admin/users/${encodeURIComponent(email)}/achievements`, { headers }).catch(() => ({ data: null })),
        axios.get(`${API}/admin/achievements?include_inactive=true`, { headers }).catch(() => ({ data: { achievements: [] } }))
      ]);
      setData(detailsRes.data);
      setUserAchievements(achievementsRes.data);
      setAllAchievements(allAchievementsRes.data.achievements || []);
    } catch (error) {
      console.error('Failed to fetch user details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignAchievement = async (achievementId) => {
    try {
      const headers = { Authorization: `Bearer ${adminToken}` };
      await axios.post(`${API}/admin/users/${encodeURIComponent(email)}/achievements/${achievementId}`, {}, { headers });
      fetchUserDetails();
    } catch (error) {
      console.error('Failed to assign achievement:', error);
    }
  };

  const handleRemoveAchievement = async (achievementId) => {
    if (!confirm('Are you sure you want to remove this achievement from the user?')) {
      return;
    }
    try {
      const headers = { Authorization: `Bearer ${adminToken}` };
      await axios.delete(`${API}/admin/users/${encodeURIComponent(email)}/achievements/${achievementId}`, { headers });
      fetchUserDetails();
    } catch (error) {
      console.error('Failed to remove achievement:', error);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <p className="text-center text-muted-foreground">Failed to load user details</p>
          <Button onClick={onClose} className="mt-4 w-full">Close</Button>
        </div>
      </div>
    );
  }

  const { user, messages, feedbacks, email_logs, activities, analytics, history } = data;
  const timezone = user?.schedule?.timezone;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-0 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-lg max-w-6xl w-full h-full sm:h-auto sm:max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 sm:p-6 border-b flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <h2 className="text-xl sm:text-2xl font-bold truncate">User Details</h2>
            <p className="text-xs sm:text-sm text-muted-foreground truncate">{email}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="ml-2 flex-shrink-0 min-h-[44px]">
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Tabs */}
        <div className="border-b px-3 sm:px-6">
          <div className="flex gap-1 sm:gap-4 overflow-x-auto scrollbar-hide">
            {['overview', 'achievements', 'messages', 'feedback', 'logs', 'activities', 'history'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2 sm:px-4 py-2 sm:py-3 border-b-2 font-medium text-xs sm:text-sm transition whitespace-nowrap min-h-[44px] ${
                  activeTab === tab
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-muted-foreground hover:text-gray-900'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-6">
          {activeTab === 'achievements' && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-yellow-500" />
                    User Achievements
                  </CardTitle>
                  <CardDescription>
                    Manage achievements for {email}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {userAchievements ? (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-lg px-3 py-1">
                          {userAchievements.total_unlocked || 0} Unlocked
                        </Badge>
                      </div>
                      
                      {/* Unlocked Achievements */}
                      {userAchievements.unlocked_achievements && userAchievements.unlocked_achievements.length > 0 ? (
                        <div>
                          <h3 className="font-semibold mb-3">Unlocked Achievements</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {userAchievements.unlocked_achievements.map((achievement) => (
                              <div key={achievement.id} className="flex items-center justify-between p-3 border rounded-lg">
                                <div className="flex items-center gap-3">
                                  <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
                                    <Trophy className="h-5 w-5" />
                                  </div>
                                  <div>
                                    <p className="font-semibold">{achievement.name}</p>
                                    <p className="text-sm text-muted-foreground">{achievement.description}</p>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleRemoveAchievement(achievement.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <p className="text-center text-muted-foreground py-8">No achievements unlocked yet</p>
                      )}

                      {/* Available Achievements to Assign */}
                      <div>
                        <h3 className="font-semibold mb-3">Assign New Achievement</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {allAchievements
                            .filter(a => a.active && (!userAchievements.achievement_ids || !userAchievements.achievement_ids.includes(a.id)))
                            .map((achievement) => (
                              <div key={achievement.id} className="flex items-center justify-between p-3 border rounded-lg">
                                <div className="flex items-center gap-3">
                                  <div className="p-2 bg-gray-100 text-gray-600 rounded-lg">
                                    <Award className="h-5 w-5" />
                                  </div>
                                  <div>
                                    <p className="font-semibold">{achievement.name}</p>
                                    <p className="text-sm text-muted-foreground">{achievement.description}</p>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleAssignAchievement(achievement.id)}
                                >
                                  Assign
                                </Button>
                              </div>
                            ))}
                        </div>
                        {allAchievements.filter(a => a.active && (!userAchievements.achievement_ids || !userAchievements.achievement_ids.includes(a.id))).length === 0 && (
                          <p className="text-center text-muted-foreground py-4">All available achievements are already assigned</p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">Loading achievements...</p>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* User Info */}
              <Card>
                <CardHeader>
                  <CardTitle>User Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Name</p>
                      <p className="font-medium">{user?.name || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Email</p>
                      <p className="font-medium">{user?.email}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Status</p>
                      <Badge className={user?.active ? 'bg-green-500' : 'bg-gray-400'}>
                        {user?.schedule?.paused ? 'Paused' : user?.active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Streak</p>
                      <p className="font-medium">{user?.streak_count || 0} days</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Total Messages</p>
                      <p className="font-medium">{user?.total_messages_received || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Created</p>
                      <p className="font-medium">
                        {user?.created_at
                          ? formatDateTimeForTimezone(user.created_at, timezone, { includeZone: true })
                          : 'N/A'}
                      </p>
                    </div>
                  </div>
                  {user?.goals && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Goals</p>
                      <p className="text-sm">{user.goals}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Analytics */}
              {analytics && (
                <Card>
                  <CardHeader>
                    <CardTitle>Analytics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Avg Rating</p>
                        <p className="text-2xl font-bold text-yellow-600">{analytics.avg_rating || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Engagement</p>
                        <p className="text-2xl font-bold text-green-600">{analytics.engagement_rate || 0}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total Messages</p>
                        <p className="text-2xl font-bold">{analytics.total_messages || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Favorite Personality</p>
                        <p className="text-lg font-medium">{analytics.favorite_personality || 'N/A'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'messages' && (
            <div className="space-y-3">
              {messages && messages.length > 0 ? (
                messages.map((msg) => (
                  <Card key={msg.id}>
                    <CardContent className="p-3 sm:p-4">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge className="text-xs">{msg.personality?.value || 'Unknown'}</Badge>
                            <span className="text-xs text-muted-foreground whitespace-nowrap">
                              {formatDateTimeForTimezone(msg.sent_at, timezone, { includeZone: true })}
                            </span>
                          </div>
                          <p className="text-xs sm:text-sm break-words">{msg.message}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8">No messages found</p>
              )}
            </div>
          )}

          {activeTab === 'feedback' && (
            <div className="space-y-3">
              {feedbacks && feedbacks.length > 0 ? (
                feedbacks.map((fb) => (
                  <Card key={fb.id}>
                    <CardContent className="p-3 sm:p-4">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`h-3 w-3 sm:h-4 sm:w-4 ${
                                  i < fb.rating
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                            <Badge className="text-xs">{fb.personality?.value || 'Unknown'}</Badge>
                          </div>
                          {fb.feedback_text && (
                            <div className="mt-2">
                              <p className="text-xs text-muted-foreground mb-1">Feedback Message:</p>
                              <p className="text-xs sm:text-sm bg-gray-50 p-2 rounded border break-words">{fb.feedback_text}</p>
                            </div>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap flex-shrink-0">
                          {formatDateTimeForTimezone(fb.created_at, timezone, { includeZone: true })}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8">No feedback found</p>
              )}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-3">
              {email_logs && email_logs.length > 0 ? (
                email_logs.map((log) => (
                  <Card key={log.id}>
                    <CardContent className="p-3 sm:p-4">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge className={`text-xs ${log.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}>
                              {log.status}
                            </Badge>
                            <p className="text-xs sm:text-sm font-medium break-words">{log.subject}</p>
                          </div>
                          {log.error_message && (
                            <p className="text-xs text-red-600 break-words">Error: {log.error_message}</p>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap flex-shrink-0">
                          {formatDateTimeForTimezone(log.sent_at || log.local_sent_at, timezone, { includeZone: true })}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8">No logs found</p>
              )}
            </div>
          )}

          {activeTab === 'activities' && (
            <div className="space-y-3">
              {activities && activities.length > 0 ? (
                activities.map((activity) => (
                  <Card key={activity.id}>
                    <CardContent className="p-3 sm:p-4">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge className="text-xs">{activity.action_type}</Badge>
                            <Badge variant="outline" className="text-xs">{activity.action_category}</Badge>
                          </div>
                          {activity.details && Object.keys(activity.details).length > 0 && (
                            <p className="text-xs text-muted-foreground break-words overflow-wrap-anywhere">
                              {Object.entries(activity.details).slice(0, 2).map(([key, value]) => (
                                <span key={key} className="block sm:inline">
                                  <span className="font-medium">{key}:</span> {typeof value === 'object' ? JSON.stringify(value).substring(0, 50) : String(value).substring(0, 50)}
                                  {Object.keys(activity.details).length > 2 && '...'}
                                </span>
                              ))}
                            </p>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap flex-shrink-0">
                          {formatDateTimeForTimezone(activity.timestamp, timezone, { includeZone: true })}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8">No activities found</p>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-3">
              {history && Object.keys(history).length > 0 ? (
                Object.entries(history).map(([key, value]) => (
                  <Card key={key}>
                    <CardHeader>
                      <CardTitle className="text-lg">{key.replace('_', ' ').toUpperCase()}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="text-xs overflow-x-auto bg-slate-50 p-2 sm:p-3 rounded break-words whitespace-pre-wrap">
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8">No history found</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

