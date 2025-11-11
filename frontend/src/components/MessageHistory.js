import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Star, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function MessageHistory({ email }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchMessages();
  }, [email]);

  const fetchMessages = async () => {
    try {
      const response = await axios.get(`${API}/users/${email}/message-history`);
      setMessages(response.data.messages);
    } catch (error) {
      toast.error("Failed to load messages");
    } finally {
      setLoading(false);
    }
  };

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
        feedback_text: feedbackText
      });
      toast.success("Thank you for your feedback!");
      setSelectedMessage(null);
      setRating(0);
      setFeedbackText("");
      fetchMessages();
    } catch (error) {
      toast.error("Failed to submit feedback");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading history...</div>;
  }

  if (messages.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">No messages yet. Your first motivation is coming soon!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <Card key={message.id} data-testid="message-history-item">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-lg">From {message.personality.value}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {new Date(message.sent_at).toLocaleDateString()} at {new Date(message.sent_at).toLocaleTimeString()}
                </p>
              </div>
              {message.rating && (
                <div className="flex items-center gap-1">
                  {[...Array(message.rating)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed whitespace-pre-wrap text-muted-foreground">
              {message.message}
            </p>
            <Dialog open={selectedMessage?.id === message.id} onOpenChange={(open) => !open && setSelectedMessage(null)}>
              <DialogTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setSelectedMessage(message)}
                  data-testid="rate-message-btn"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  {message.rating ? 'Update Rating' : 'Rate This Message'}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Rate This Message</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">How inspiring was this message?</label>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => setRating(star)}
                          className="transition-transform hover:scale-110"
                          data-testid={`star-${star}`}
                        >
                          <Star 
                            className={`h-8 w-8 ${
                              star <= rating 
                                ? 'fill-yellow-400 text-yellow-400' 
                                : 'text-gray-300'
                            }`}
                          />
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Additional Feedback (Optional)</label>
                    <Textarea
                      placeholder="What did you like or what could be improved?"
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      rows={3}
                    />
                  </div>
                  <Button 
                    onClick={submitFeedback} 
                    disabled={submitting || rating === 0}
                    className="w-full"
                    data-testid="submit-feedback-btn"
                  >
                    {submitting ? 'Submitting...' : 'Submit Feedback'}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}