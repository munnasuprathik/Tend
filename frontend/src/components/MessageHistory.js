import { useState, useEffect, useMemo, useCallback } from "react";
import React from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LiquidButton as Button } from "@/components/animate-ui/components/buttons/liquid";
import { Input } from "@/components/ui/input";
import { Star, MessageSquare, Loader2, User, Clock, Search, X, Heart, Download, Reply, CheckCircle2, Filter, Calendar } from "lucide-react";
import { exportMessageHistory } from "@/utils/exportData";
import { toast } from "sonner";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/animate-ui/components/radix/dialog";
import { formatDateTimeForTimezone } from "@/utils/timezoneFormatting";
import { SkeletonLoader } from "@/components/SkeletonLoader";
import { retryWithBackoff } from "@/utils/retry";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

// Use centralized API configuration
import API_CONFIG from '@/config/api';
const API = API_CONFIG.API_BASE;

export const MessageHistory = React.memo(function MessageHistory({ email, timezone, refreshKey = 0, onFeedbackSubmitted }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");
  const [filterRating, setFilterRating] = useState(null);
  const [favoriteMessages, setFavoriteMessages] = useState([]);
  const [stats, setStats] = useState({ sent_count: 0, reply_count: 0 });

  const fetchMessages = useCallback(async () => {
    try {
      setLoading(true);
      const response = await retryWithBackoff(async () => {
        return await axios.get(`${API}/users/${email}/message-history`);
      });
      setMessages(response.data.messages || []);
      setStats({
        sent_count: response.data.sent_count || 0,
        reply_count: response.data.reply_count || 0
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to load messages");
    } finally {
      setLoading(false);
    }
  }, [email]);

  const fetchFavorites = useCallback(async () => {
    try {
      const user = await axios.get(`${API}/users/${email}`);
      setFavoriteMessages(user.data.favorite_messages || []);
    } catch (error) {
      // Silently fail - favorites are optional
    }
  }, [email]);

  useEffect(() => {
    fetchMessages();
    fetchFavorites();
  }, [email, refreshKey, fetchMessages, fetchFavorites]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchMessages();
      fetchFavorites();
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchMessages, fetchFavorites]);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const toggleFavorite = async (messageId) => {
    try {
      const response = await axios.post(`${API}/users/${email}/messages/${messageId}/favorite`);
      setFavoriteMessages(prev => {
        if (response.data.is_favorite) {
          return [...prev, messageId];
        } else {
          return prev.filter(id => id !== messageId);
        }
      });
      toast.success(response.data.is_favorite ? "Added to favorites" : "Removed from favorites");
    } catch (error) {
      toast.error("Failed to update favorite");
    }
  };

  // Group messages with their replies
  const groupedMessages = useMemo(() => {
    const sentMessages = messages.filter(m => m.type === "sent");
    const replyMessages = messages.filter(m => m.type === "reply");
    
    const repliesMap = new Map();
    replyMessages.forEach(reply => {
      const linkedMessageId = reply.linked_message_id;
      if (linkedMessageId) {
        if (!repliesMap.has(linkedMessageId)) {
          repliesMap.set(linkedMessageId, []);
        }
        repliesMap.get(linkedMessageId).push(reply);
      } else {
        const replyTime = new Date(reply.sent_at);
        const matchingMessage = sentMessages
          .filter(m => {
            const msgTime = new Date(m.sent_at);
            return msgTime < replyTime;
          })
          .sort((a, b) => new Date(b.sent_at) - new Date(a.sent_at))[0];
        
        if (matchingMessage) {
          if (!repliesMap.has(matchingMessage.id)) {
            repliesMap.set(matchingMessage.id, []);
          }
          repliesMap.get(matchingMessage.id).push(reply);
        }
      }
    });
    
    repliesMap.forEach((replies, msgId) => {
      replies.sort((a, b) => new Date(b.sent_at) - new Date(a.sent_at));
    });
    
    const grouped = sentMessages.map(msg => ({
      ...msg,
      replies: (repliesMap.get(msg.id) || []).sort((a, b) => new Date(a.sent_at) - new Date(b.sent_at))
    })).sort((a, b) => new Date(b.sent_at) - new Date(a.sent_at));
    
    return grouped;
  }, [messages]);

  // Filter and search messages
  const filteredMessages = useMemo(() => {
    return groupedMessages.filter((group) => {
      const message = group;
      const matchesSearch = !debouncedSearchQuery || 
        message.message?.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        message.personality?.value?.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        message.subject?.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        (message.replies?.some(r => r.message?.toLowerCase().includes(debouncedSearchQuery.toLowerCase())));
      
      const matchesRating = filterRating === null || message.rating === filterRating;
      
      return matchesSearch && matchesRating;
    });
  }, [groupedMessages, debouncedSearchQuery, filterRating]);

  // Group messages by date
  const messagesByDate = useMemo(() => {
    const groups = {};
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const thisWeek = new Date(today);
    thisWeek.setDate(thisWeek.getDate() - 7);
    const thisMonth = new Date(today);
    thisMonth.setMonth(thisMonth.getMonth() - 1);

    filteredMessages.forEach((message) => {
      const msgDate = new Date(message.sent_at);
      const msgDateOnly = new Date(msgDate.getFullYear(), msgDate.getMonth(), msgDate.getDate());
      
      let groupKey;
      if (msgDateOnly.getTime() === today.getTime()) {
        groupKey = 'Today';
      } else if (msgDateOnly.getTime() === yesterday.getTime()) {
        groupKey = 'Yesterday';
      } else if (msgDate >= thisWeek) {
        groupKey = 'This Week';
      } else if (msgDate >= thisMonth) {
        groupKey = 'This Month';
      } else {
        groupKey = msgDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      }

      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(message);
    });

    // Sort groups by date (most recent first)
    const sortedGroups = Object.entries(groups).sort((a, b) => {
      const order = ['Today', 'Yesterday', 'This Week', 'This Month'];
      const aIndex = order.indexOf(a[0]);
      const bIndex = order.indexOf(b[0]);
      if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
      if (aIndex !== -1) return -1;
      if (bIndex !== -1) return 1;
      return new Date(b[1][0].sent_at) - new Date(a[1][0].sent_at);
    });

    return sortedGroups;
  }, [filteredMessages]);

  const submitFeedback = async () => {
    if (rating === 0) {
      toast.error("Please select a rating");
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/users/${email}/feedback`, {
        message_id: selectedMessage?.id,
        rating,
        feedback_text: feedbackText,
        personality: selectedMessage?.personality,
      });
      toast.success("Thank you for your feedback!");
      setSelectedMessage(null);
      setRating(0);
      setFeedbackText("");
      fetchMessages();
      if (typeof onFeedbackSubmitted === "function") {
        onFeedbackSubmitted();
      }
    } catch (error) {
      toast.error("Failed to submit feedback");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonLoader variant="card" count={3} />
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <Card className="border border-border/30 bg-card/50 backdrop-blur-sm">
        <CardContent className="py-20 text-center">
          <div className="flex flex-col items-center">
            <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-muted/50 to-muted/30 border border-border/30 flex items-center justify-center mb-5">
              <MessageSquare className="h-10 w-10 text-muted-foreground/50" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-foreground">No messages yet</h3>
            <p className="text-sm text-muted-foreground max-w-md leading-relaxed">
              Your first motivational message is coming soon! Make sure your schedule is active in Settings.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards - Compact Design with Visual Indicators */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-3 sm:mb-2">
          <Card className="border border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-blue-400/3 hover:border-blue-500/30 hover:shadow-md transition-all duration-300 group">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 sm:gap-2.5">
                  <div className="p-1.5 sm:p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 group-hover:bg-blue-500/15 transition-colors">
                    <MessageSquare className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-500" />
                  </div>
                  <p className="text-xs font-semibold text-blue-600/70 dark:text-blue-400/70 uppercase tracking-wider">Total Messages</p>
                </div>
              </div>
              <div className="space-y-1.5">
                <p className="text-3xl font-bold tracking-tight text-foreground">{stats.sent_count}</p>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1 bg-blue-500/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${Math.min(100, (stats.sent_count / 100) * 100)}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-muted-foreground font-medium">All time</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-green-500/20 bg-gradient-to-br from-green-500/5 to-green-400/3 hover:border-green-500/30 hover:shadow-md transition-all duration-300 group">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 sm:gap-2.5">
                  <div className="p-1.5 sm:p-2 rounded-lg bg-green-500/10 border border-green-500/20 group-hover:bg-green-500/15 transition-colors">
                    <Reply className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-green-500" />
                  </div>
                  <p className="text-xs font-semibold text-green-600/70 dark:text-green-400/70 uppercase tracking-wider">Replies</p>
                </div>
              </div>
              <div className="space-y-1.5">
                <p className="text-3xl font-bold tracking-tight text-foreground">{stats.reply_count}</p>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1 bg-green-500/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${stats.sent_count > 0 ? Math.min(100, (stats.reply_count / stats.sent_count) * 100) : 0}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-muted-foreground font-medium">
                    {stats.sent_count > 0 ? `${Math.round((stats.reply_count / stats.sent_count) * 100)}% rate` : 'No replies'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-purple-400/3 hover:border-purple-500/30 hover:shadow-md transition-all duration-300 group">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 sm:gap-2.5">
                  <div className="p-1.5 sm:p-2 rounded-lg bg-purple-500/10 border border-purple-500/20 group-hover:bg-purple-500/15 transition-colors">
                    <Filter className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-purple-500" />
                  </div>
                  <p className="text-xs font-semibold text-purple-600/70 dark:text-purple-400/70 uppercase tracking-wider">Showing</p>
                </div>
              </div>
              <div className="space-y-1.5">
                <p className="text-3xl font-bold tracking-tight text-foreground">{filteredMessages.length}</p>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1 bg-purple-500/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500 rounded-full"
                      style={{ width: `${messages.length > 0 ? Math.min(100, (filteredMessages.length / messages.length) * 100) : 0}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-muted-foreground font-medium">
                    {filteredMessages.length === messages.length ? 'All' : 'Filtered'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

      {/* Filters and Search */}
      <Card className="border border-border/30 hover:border-border/50 transition-all duration-300">
        <CardContent className="p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-3.5 w-3.5 sm:h-4 sm:w-4 text-muted-foreground" />
              <Input
                placeholder="Search messages, personalities, or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-9 h-10"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                </button>
              )}
            </div>

            {/* Rating Filter */}
            <Select value={filterRating?.toString() || "all"} onValueChange={(value) => setFilterRating(value === "all" ? null : Number(value))}>
              <SelectTrigger className="w-full sm:w-[180px] h-10">
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <Star className="h-3.5 w-3.5 sm:h-4 sm:w-4 flex-shrink-0" />
                  <SelectValue placeholder="Filter by rating" />
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Ratings</SelectItem>
                <SelectItem value="5">5 Stars</SelectItem>
                <SelectItem value="4">4 Stars</SelectItem>
                <SelectItem value="3">3 Stars</SelectItem>
                <SelectItem value="2">2 Stars</SelectItem>
                <SelectItem value="1">1 Star</SelectItem>
                <SelectItem value="0">Unrated</SelectItem>
              </SelectContent>
            </Select>

            {/* Export Button */}
            <Button
              variant="outline"
              onClick={() => exportMessageHistory(messages)}
              className="h-11 sm:h-10 shrink-0 touch-manipulation"
            >
              <Download className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              <span className="hidden sm:inline">Export</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Messages List */}
      {filteredMessages.length === 0 && messages.length > 0 ? (
        <Card className="border border-border/30 bg-card/50 backdrop-blur-sm">
          <CardContent className="py-16 text-center">
            <div className="flex flex-col items-center">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-muted/50 to-muted/30 border border-border/30 flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-muted-foreground/50" />
              </div>
              <p className="text-base font-semibold mb-1.5 text-foreground">No messages found</p>
              <p className="text-sm text-muted-foreground leading-relaxed">Try adjusting your search or filter criteria.</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {messagesByDate.map(([dateGroup, messages]) => (
            <div key={dateGroup} className="space-y-4">
              {/* Date Group Header */}
              <div className="flex items-center gap-2 sm:gap-3 sticky top-0 z-10 bg-background/80 backdrop-blur-sm py-2 -mt-2">
                <div className="h-px flex-1 bg-border" />
                <div className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 flex-shrink-0">
                  <Calendar className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-muted-foreground flex-shrink-0" />
                  <span className="text-xs sm:text-sm font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap">{dateGroup}</span>
                  <Badge variant="secondary" className="text-xs flex-shrink-0">{messages.length}</Badge>
                </div>
                <div className="h-px flex-1 bg-border" />
              </div>
              
              {/* Messages in this date group */}
              {messages.map((message) => {
            const hasReplies = message.replies && message.replies.length > 0;
            const isFavorite = favoriteMessages.includes(message.id);
            
            return (
              <div key={message.id} className="space-y-3">
                {/* Main Message Card */}
                <Card 
                  data-testid="message-history-item" 
                  className={cn(
                    "group hover:shadow-md transition-all duration-300 border border-border/30 hover:border-border/50",
                    hasReplies && "border-2 border-border/40"
                  )}
                >
                  <CardHeader className="pb-3 sm:pb-4">
                    <div className="flex items-center justify-between gap-2 sm:gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 sm:gap-3 mb-2.5 sm:mb-3">
                          <div className="p-1.5 sm:p-2 rounded-lg bg-muted group-hover:bg-accent transition-colors flex-shrink-0">
                            <User className="h-4 w-4 sm:h-5 sm:w-5 text-foreground" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <CardTitle className="text-base sm:text-lg font-semibold mb-1 leading-tight">
                              {message.personality?.value || "Unknown Personality"}
                            </CardTitle>
                            <div className="flex items-center gap-1 sm:gap-1.5 text-xs sm:text-sm text-muted-foreground">
                              <Clock className="h-3 w-3 sm:h-3.5 sm:w-3.5 flex-shrink-0" />
                              <span className="truncate">{formatDateTimeForTimezone(message.sent_at, timezone)}</span>
                            </div>
                          </div>
                        </div>

                        {/* Badges */}
                        <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap mt-1">
                          {hasReplies && (
                            <Badge variant="outline" className="gap-1 sm:gap-1.5 text-xs items-center">
                              <CheckCircle2 className="h-2.5 w-2.5 sm:h-3 sm:w-3 flex-shrink-0" />
                              <span>{message.replies.length === 1 ? 'Replied' : `${message.replies.length} replies`}</span>
                            </Badge>
                          )}
                          {message.used_fallback && (
                            <Badge variant="outline" className="text-xs">Backup</Badge>
                          )}
                          {message.rating && (
                            <div className="flex items-center gap-0.5 sm:gap-1">
                              {[...Array(message.rating)].map((_, i) => (
                                <Star key={i} className="h-3 w-3 sm:h-4 sm:w-4 fill-foreground text-foreground flex-shrink-0" />
                              ))}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => toggleFavorite(message.id)}
                          className="h-9 w-9 sm:h-9 sm:w-9 touch-manipulation"
                        >
                          <Heart
                            className={cn(
                              "h-3.5 w-3.5 sm:h-4 sm:w-4 transition-colors",
                              isFavorite ? "fill-foreground text-foreground" : "text-muted-foreground hover:text-foreground"
                            )}
                          />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-3 sm:space-y-4 pt-0">
                    {/* Message Content */}
                    <div className="rounded-lg p-3 sm:p-4 bg-muted/50 border border-border">
                      <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground break-words">
                        {message.message}
                      </p>
                    </div>

                    {/* Rate Button */}
                    <Dialog open={selectedMessage?.id === message.id} onOpenChange={(open) => !open && setSelectedMessage(null)}>
                      <DialogTrigger asChild>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => {
                            setSelectedMessage(message);
                            setRating(message.rating || 0);
                            setFeedbackText("");
                          }}
                          data-testid="rate-message-btn"
                          className="w-full sm:w-auto h-11 sm:h-9 touch-manipulation"
                        >
                          <Star className={cn("h-3.5 w-3.5 sm:h-4 sm:w-4", message.rating && "fill-foreground text-foreground")} />
                          {message.rating ? 'Update Rating' : 'Rate This Message'}
                        </Button>
                      </DialogTrigger>
                      <DialogContent from="top" showCloseButton={true} className="w-[95vw] max-w-md sm:max-w-[500px] p-5 sm:p-6 max-h-[90vh] overflow-y-auto rounded-2xl">
                        <DialogHeader className="pb-2">
                          <DialogTitle className="text-xl sm:text-2xl text-center">Rate This Message</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-6 pt-2">
                          <div className="text-center">
                            <label className="text-base font-medium mb-4 block text-muted-foreground">How inspiring was this message?</label>
                            <div className="flex gap-1.5 justify-center touch-none py-2 flex-nowrap w-full overflow-x-hidden">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <button
                                  key={star}
                                  onClick={() => setRating(star)}
                                  className="transition-transform hover:scale-110 active:scale-90 p-1.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-full flex-shrink-0"
                                  type="button"
                                >
                                  <Star 
                                    className={cn(
                                      "h-8 w-8 sm:h-10 sm:w-10 transition-colors duration-200",
                                      star <= rating 
                                        ? 'fill-amber-400 text-amber-400' 
                                        : 'text-muted-foreground/20 hover:text-amber-400/50'
                                    )}
                                  />
                                </button>
                              ))}
                            </div>
                          </div>
                          <div className="space-y-2">
                            <label className="text-sm font-medium block">Additional Feedback (Optional)</label>
                            <Textarea
                              placeholder="What did you like or what could be improved?"
                              value={feedbackText}
                              onChange={(e) => setFeedbackText(e.target.value)}
                              rows={4}
                              className="resize-none text-base min-h-[120px] p-3"
                            />
                          </div>
                          <Button 
                            onClick={submitFeedback} 
                            disabled={submitting || rating === 0}
                            className="w-full h-12 sm:h-11 text-base font-medium shadow-sm mt-2 touch-manipulation"
                          >
                            {submitting ? (
                              <>
                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                Submitting...
                              </>
                            ) : (
                              'Submit Feedback'
                            )}
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </CardContent>
                </Card>
                
                {/* Replies Section */}
                {hasReplies && (
                  <div className="ml-0 sm:ml-8 space-y-3 pl-0 sm:pl-4">
                    <div className="flex items-center gap-1.5 sm:gap-2 mb-2">
                      <Reply className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-muted-foreground flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-muted-foreground">
                        {message.replies.length === 1 ? 'Your Reply' : 'Your Replies'}
                      </span>
                    </div>
                    {message.replies.map((reply) => (
                      <Card 
                        key={reply.id}
                        className="bg-muted/30 border-border hover:shadow-md transition-shadow"
                      >
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5 sm:gap-2">
                              <div className="p-1.5 rounded-lg bg-muted flex-shrink-0">
                                <Reply className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-foreground" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <CardTitle className="text-xs sm:text-sm font-semibold">Your Reply</CardTitle>
                                <div className="flex items-center gap-1.5 sm:gap-2 text-xs text-muted-foreground mt-0.5">
                                  <Clock className="h-2.5 w-2.5 sm:h-3 sm:w-3 flex-shrink-0" />
                                  <span className="truncate">{formatDateTimeForTimezone(reply.sent_at, timezone)}</span>
                                </div>
                              </div>
                            </div>
                            {reply.reply_sentiment && (
                              <Badge variant="outline" className="text-xs">
                                {reply.reply_sentiment}
                              </Badge>
                            )}
                          </div>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <div className="rounded-lg p-3 bg-background border border-border">
                            <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground">
                              {reply.message}
                            </p>
                          </div>
                          
                          {/* Insights */}
                          {(reply.extracted_wins?.length > 0 || reply.extracted_struggles?.length > 0) && (
                            <div className="mt-3 p-3 rounded-lg bg-muted/50 border border-border">
                              <p className="text-xs font-semibold text-foreground mb-2">Insights</p>
                              {reply.extracted_wins?.length > 0 && (
                                <div className="mb-2">
                                  <p className="text-xs font-medium text-foreground mb-1">Wins</p>
                                  <ul className="text-xs text-muted-foreground list-disc list-inside space-y-0.5">
                                    {reply.extracted_wins.map((win, idx) => (
                                      <li key={idx}>{win}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {reply.extracted_struggles?.length > 0 && (
                                <div>
                                  <p className="text-xs font-medium text-foreground mb-1">Struggles</p>
                                  <ul className="text-xs text-muted-foreground list-disc list-inside space-y-0.5">
                                    {reply.extracted_struggles.map((struggle, idx) => (
                                      <li key={idx}>{struggle}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
});
