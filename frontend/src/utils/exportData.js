/**
 * Utility functions for exporting user data to CSV/PDF formats
 */

/**
 * Export data to CSV format
 */
export const exportToCSV = (data, filename, headers = null) => {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  // Use provided headers or extract from first object
  const csvHeaders = headers || Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    // Header row
    csvHeaders.join(','),
    // Data rows
    ...data.map(row => 
      csvHeaders.map(header => {
        const value = row[header];
        // Handle values that might contain commas or quotes
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        // Escape quotes and wrap in quotes if contains comma, quote, or newline
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
};

/**
 * Export message history to CSV
 */
export const exportMessageHistory = (messages) => {
  if (!messages || messages.length === 0) {
    return;
  }

  const csvData = messages.map(msg => ({
    'Date': msg.sent_at ? new Date(msg.sent_at).toLocaleDateString() : 'N/A',
    'Time': msg.sent_at ? new Date(msg.sent_at).toLocaleTimeString() : 'N/A',
    'Subject': msg.subject || 'N/A',
    'Message': (msg.message || '').replace(/\n/g, ' ').substring(0, 500),
    'Personality': msg.personality?.value || msg.personality || 'N/A',
    'Streak at Time': msg.streak_at_time || 'N/A',
    'Message Type': msg.message_type || 'N/A',
    'Favorite': msg.is_favorite ? 'Yes' : 'No'
  }));

  exportToCSV(csvData, `message-history-${new Date().toISOString().split('T')[0]}`);
};

/**
 * Export achievements to CSV
 */
export const exportAchievements = (achievements) => {
  if (!achievements) {
    return;
  }

  const allAchievements = [
    ...(achievements.unlocked || []).map(ach => ({
      'Name': ach.name,
      'Description': ach.description,
      'Category': ach.category || 'N/A',
      'Status': 'Unlocked',
      'Unlocked At': ach.unlocked_at ? new Date(ach.unlocked_at).toLocaleDateString() : 'N/A'
    })),
    ...(achievements.locked || []).map(ach => ({
      'Name': ach.name,
      'Description': ach.description,
      'Category': ach.category || 'N/A',
      'Status': 'Locked',
      'Unlocked At': 'N/A'
    }))
  ];

  if (allAchievements.length === 0) {
    return;
  }

  exportToCSV(allAchievements, `achievements-${new Date().toISOString().split('T')[0]}`);
};

/**
 * Export analytics summary to CSV
 */
export const exportAnalytics = (user, analytics) => {
  if (!user) {
    return;
  }

  const analyticsData = [{
    'Total Messages': user.total_messages_received || 0,
    'Current Streak': user.streak_count || 0,
    'Longest Streak': analytics?.longest_streak || user.streak_count || 0,
    'Account Created': user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A',
    'Last Email Sent': user.last_email_sent ? new Date(user.last_email_sent).toLocaleDateString() : 'N/A',
    'Total Achievements': analytics?.total_achievements || 0,
    'Unlocked Achievements': analytics?.unlocked_achievements || 0,
    'Best Day of Week': analytics?.best_day || 'N/A',
    'Average Messages per Week': analytics?.avg_messages_per_week?.toFixed(2) || '0'
  }];

  exportToCSV(analyticsData, `analytics-summary-${new Date().toISOString().split('T')[0]}`);
};

