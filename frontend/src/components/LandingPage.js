import React, { useState, useEffect } from 'react';
import { Mail, Sparkles, Clock, Users, Zap, CheckCircle, Star, TrendingUp, Brain, Heart, Target, ArrowRight, Play } from 'lucide-react';
import { LiquidButton as Button } from "@/components/animate-ui/components/buttons/liquid";
import { Card, CardContent } from "@/components/ui/card";
import { ROUTES, getRouteUrl } from '@/config/routes';

// Dynamic URL configuration - uses route configuration
const REDIRECT_URL = getRouteUrl(ROUTES.DASHBOARD.path);
const AUTH_URL = getRouteUrl(ROUTES.HOME.path) + `?redirect=${encodeURIComponent(REDIRECT_URL)}`;

export function LandingPage({ onNavigate }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSignIn = () => {
    window.location.href = AUTH_URL;
  };

  return (
    <div className="min-h-screen bg-background font-sans">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled ? 'bg-background/80 backdrop-blur-lg border-b border-border/50' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 bg-gradient-to-br from-primary to-primary/80 rounded-xl flex items-center justify-center shadow-sm">
                <Sparkles className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-foreground tracking-tight">
                Tend
              </span>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => onNavigate && onNavigate('admin')}
                className="text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50"
              >
                Admin
              </Button>
              <Button
                onClick={handleSignIn}
                className="bg-primary hover:bg-primary/90 text-primary-foreground h-9 px-4 text-sm font-medium shadow-sm"
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 relative overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/5 rounded-full blur-[120px] opacity-50" />
          <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-blue-500/5 rounded-full blur-[120px] opacity-30" />
          <div className="absolute inset-0 bg-grid-pattern opacity-[0.02]" />
        </div>

        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
                <span className="text-xs font-medium text-primary">AI-Powered Daily Motivation</span>
              </div>
              
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-[1.1] tracking-tight text-foreground">
                Wake up to
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-600 pb-2">
                  personalized
                </span>
                inspiration.
              </h1>
              
              <p className="text-lg sm:text-xl text-muted-foreground leading-relaxed max-w-2xl font-light">
                Get unique, never-repeating AI motivation emails tailored to your specific goals and schedule. 
                Delivered exactly when you need them.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  onClick={handleSignIn}
                  size="lg"
                  className="bg-primary hover:bg-primary/90 text-primary-foreground text-base h-12 px-8 shadow-lg shadow-primary/25"
                >
                  <Mail className="mr-2 h-4 w-4" />
                  Start Free Today
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  className="h-12 px-8 text-base bg-background/50 backdrop-blur-sm hover:bg-accent/50"
                  onClick={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}
                >
                  <Play className="mr-2 h-4 w-4" />
                  How it Works
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-x-8 gap-y-3 pt-4 border-t border-border/50">
                {["Free forever", "No credit card", "2 min setup"].map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative lg:ml-auto w-full max-w-md lg:max-w-full">
              <div className="relative z-10">
                <Card className="border-border/40 shadow-2xl bg-card/80 backdrop-blur-md">
                  <CardContent className="p-6 sm:p-8 space-y-6">
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                        <Star className="h-5 w-5 text-primary-foreground" />
                      </div>
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">15 Day Streak</p>
                          <span className="text-xs text-muted-foreground">9:00 AM</span>
                        </div>
                        <p className="font-semibold text-foreground">Good morning, Sarah! 👋</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4 pl-14">
                      <div className="p-4 rounded-2xl bg-muted/50 border border-border/50">
                        <p className="text-foreground/90 text-sm leading-relaxed">
                          "Remember when you thought launching that side project was impossible? 
                          You're 15 days in now. That's 15 days of showing up when it was easier to quit.
                          The momentum is on your side today."
                        </p>
                      </div>
                      <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        Inspired by Elon Musk
                      </div>
                    </div>

                    <div className="pt-4 border-t border-border/50">
                      <p className="text-sm font-medium text-foreground mb-2">Daily Reflection</p>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="flex-1 text-xs h-8 bg-background">
                          I'm ready! 🚀
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 text-xs h-8 bg-background">
                          Need focus 🎯
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Decor Elements */}
              <div className="absolute -top-12 -right-12 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl animate-pulse" />
              <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-primary/10 rounded-full blur-2xl animate-pulse delay-700" />
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 border-y border-border/40 bg-muted/20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { icon: Users, value: "10K+", label: "Active Users" },
              { icon: Mail, value: "500K+", label: "Emails Sent" },
              { icon: TrendingUp, value: "94%", label: "Open Rate" },
              { icon: Star, value: "4.9/5", label: "User Rating" }
            ].map((stat, i) => (
              <div key={i} className="text-center group cursor-default">
                <div className="inline-flex items-center justify-center w-10 h-10 bg-background border border-border/50 rounded-lg mb-3 shadow-sm group-hover:border-primary/30 group-hover:scale-110 transition-all duration-300">
                  <stat.icon className="h-5 w-5 text-primary" />
                </div>
                <div className="text-2xl font-bold text-foreground mb-0.5">{stat.value}</div>
                <div className="text-xs text-muted-foreground font-medium uppercase tracking-wide">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight">
              Why Tend is
              <span className="text-primary"> Different</span>
            </h2>
            <p className="text-lg text-muted-foreground">
              Not just another generic newsletter. Every email is unique, personal, and perfectly timed for YOU.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Sparkles,
                title: "Never Repeats",
                desc: "AI generates completely unique content every single day. No templates, no repetition.",
                color: "bg-orange-500/10 text-orange-500"
              },
              {
                icon: Brain,
                title: "AI Personalities",
                desc: "Choose from Elon Musk, Oprah, Steve Jobs, or create custom voices. Messages feel authentic.",
                color: "bg-purple-500/10 text-purple-500"
              },
              {
                icon: Clock,
                title: "Your Perfect Time",
                desc: "9 AM in New York? 11 PM in Tokyo? Set your ideal time, we handle all timezones.",
                color: "bg-blue-500/10 text-blue-500"
              },
              {
                icon: Target,
                title: "Goal-Focused",
                desc: "References YOUR specific goals creatively - never copy-pasted, always relevant.",
                color: "bg-green-500/10 text-green-500"
              },
              {
                icon: Heart,
                title: "Engaging Questions",
                desc: "Every email ends with thought-provoking questions to make you actually think and respond.",
                color: "bg-red-500/10 text-red-500"
              },
              {
                icon: Zap,
                title: "Streak Tracking",
                desc: "Visual streak counter celebrates your consistency with milestone rewards.",
                color: "bg-yellow-500/10 text-yellow-500"
              }
            ].map((feature, i) => (
              <Card key={i} className="border border-border/40 hover:border-border/80 hover:shadow-lg transition-all duration-300 bg-card/50 backdrop-blur-sm group">
                <CardContent className="p-6 space-y-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${feature.color} transition-transform duration-300 group-hover:scale-110`}>
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-foreground mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{feature.desc}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-4 bg-muted/20 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.03]" />
        <div className="max-w-5xl mx-auto relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight">
              Get Started in
              <span className="text-primary"> 3 Easy Steps</span>
            </h2>
          </div>

          <div className="space-y-6">
            {[
              {
                step: "01",
                title: "Sign Up with Google",
                desc: "One-click authentication. No passwords to remember.",
                icon: Users
              },
              {
                step: "02",
                title: "Set Your Preferences",
                desc: "Choose your goals, personality style, and perfect delivery time.",
                icon: Target
              },
              {
                step: "03",
                title: "Receive Daily Inspiration",
                desc: "Wake up to unique, personalized motivation tailored just for you.",
                icon: Mail
              }
            ].map((step, i) => (
              <div key={i} className="flex gap-6 items-center p-6 rounded-2xl bg-background/50 border border-border/40 hover:border-primary/20 hover:shadow-sm transition-all duration-300">
                <div className="flex-shrink-0 w-14 h-14 bg-background rounded-xl border border-border flex items-center justify-center shadow-sm">
                  <span className="text-xl font-bold text-primary">{step.step}</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold mb-1 text-foreground">{step.title}</h3>
                  <p className="text-muted-foreground">{step.desc}</p>
                </div>
                <div className="hidden sm:block p-3 bg-primary/5 rounded-full">
                  <step.icon className="h-5 w-5 text-primary" />
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Button
              onClick={handleSignIn}
              size="lg"
              className="bg-primary hover:bg-primary/90 text-primary-foreground text-base h-14 px-10 shadow-lg shadow-primary/20"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Start Your Journey Now
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center relative">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-blue-600/20 rounded-3xl blur-3xl opacity-20" />
          <Card className="bg-primary text-primary-foreground border-0 shadow-2xl relative overflow-hidden">
            <div className="absolute inset-0 bg-grid-white/[0.1]" />
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
            
            <CardContent className="p-12 sm:p-16 space-y-8 relative z-10">
              <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
                Ready to Transform Your Mornings?
              </h2>
              <p className="text-xl text-primary-foreground/80 max-w-2xl mx-auto font-light">
                Join thousands who start their day with purpose, motivation, and clarity.
              </p>
              <div className="pt-4">
                <Button
                  onClick={handleSignIn}
                  size="lg"
                  className="bg-background text-foreground hover:bg-background/90 text-base h-14 px-10 shadow-lg border-0"
                >
                  Get Started Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
              <p className="text-sm text-primary-foreground/60">
                No credit card required • 2-minute setup • Free forever
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-background border-t border-border/40 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <span className="text-lg font-bold text-foreground">Tend</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
              <a href="#" className="hover:text-foreground transition-colors">Terms</a>
              <a href="#" className="hover:text-foreground transition-colors">Contact</a>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 Tend. Motivation delivered daily.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
