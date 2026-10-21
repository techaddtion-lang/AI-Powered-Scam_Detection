import axios from 'axios';

// Use environment variable if provided, fallback to relative API proxy or localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const apiService = {
  /**
   * Analyze an SMS, Email, or text message.
   */
  async analyzeMessage(text, senderId = null, channel = 'sms') {
    const response = await apiClient.post('/analyze-message', {
      text,
      sender_id: senderId,
      channel,
    });
    return response.data;
  },

  /**
   * Analyze a phone call audio transcript.
   */
  async analyzeCall(transcript, callerNumber = null, durationSeconds = null) {
    const response = await apiClient.post('/analyze-call', {
      transcript,
      caller_number: callerNumber,
      call_duration_seconds: durationSeconds ? parseInt(durationSeconds, 10) : null,
    });
    return response.data;
  },

  /**
   * Direct URL security inspection.
   */
  async analyzeUrl(url) {
    const response = await apiClient.post('/analyze-url', { url });
    return response.data;
  },

  /**
   * Fetch real-time analytics from MySQL database.
   */
  async getAnalyticsOverview() {
    const response = await apiClient.get('/analytics/overview');
    return response.data;
  },

  /**
   * Fetch historical scan audit records from MySQL.
   */
  async getScanHistory(limit = 25, classification = null) {
    const params = { limit };
    if (classification) params.classification = classification;
    const response = await apiClient.get('/scans/history', { params });
    return response.data;
  },

  /**
   * Fetch phone & domain threat intelligence from MySQL.
   */
  async getThreatBlacklist() {
    const response = await apiClient.get('/intelligence/blacklist');
    return response.data;
  },

  /**
   * Report a new threat to MySQL database.
   */
  async reportThreat(threatData) {
    const response = await apiClient.post('/intelligence/report-threat', threatData);
    return response.data;
  },

  /**
   * Submit analyst feedback (true/false positive) to MySQL.
   */
  async submitFeedback(scanId, feedbackType, comments = null) {
    const response = await apiClient.post('/feedback', {
      scan_id: scanId,
      feedback_type: feedbackType,
      comments,
    });
    return response.data;
  },

  /**
   * Batch message analysis.
   */
  async batchAnalyze(messages) {
    const response = await apiClient.post('/batch-analyze', {
      messages: messages.map((m) => (typeof m === 'string' ? { text: m } : m)),
    });
    return response.data;
  },

  /**
   * Fetch ready-to-test preset samples.
   */
  async getSamples() {
    const response = await apiClient.get('/samples');
    return response.data;
  },

  /**
   * Check backend health and ML status.
   */
  async checkHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Request model retraining on the backend.
   */
  async retrainModel() {
    const response = await apiClient.post('/model/retrain');
    return response.data;
  },
};

export default apiService;
