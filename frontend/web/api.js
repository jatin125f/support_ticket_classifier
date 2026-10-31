/**
 * Centralized API configuration and client utilities for AI SupportDesk.
 * Automatically resolves the backend host depending on whether the frontend
 * is served directly by FastAPI static files or via a separate dev server.
 */
const API_BASE_URL = window.API_BASE_URL || (
  window.location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : (window.location.port === "8000" || window.location.pathname.startsWith("/app")
        ? window.location.origin
        : "http://127.0.0.1:8000")
);

const API = {
  baseUrl: API_BASE_URL,

  async getHealth() {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async getTickets(params = {}) {
    const query = new URLSearchParams();
    if (params.category && params.category !== "All Categories") query.append("category", params.category);
    if (params.priority && params.priority !== "All Priorities") query.append("priority", params.priority);
    if (params.status && params.status !== "All Statuses") query.append("status", params.status);
    if (params.search && params.search.trim()) query.append("search", params.search.trim());

    const qs = query.toString() ? `?${query.toString()}` : "";
    const res = await fetch(`${API_BASE_URL}/tickets${qs}`);
    if (!res.ok) throw new Error(`Failed to fetch tickets: HTTP ${res.status}`);
    return res.json();
  },

  async getTicket(id) {
    const res = await fetch(`${API_BASE_URL}/tickets/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch ticket ${id}: HTTP ${res.status}`);
    return res.json();
  },

  async createTicket(text) {
    const res = await fetch(`${API_BASE_URL}/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to create ticket" }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  async updateTicketStatus(id, status) {
    const res = await fetch(`${API_BASE_URL}/tickets/${id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to update status" }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  async getAnalytics() {
    const res = await fetch(`${API_BASE_URL}/analytics`);
    if (!res.ok) throw new Error(`Failed to fetch analytics: HTTP ${res.status}`);
    return res.json();
  },

  async getKnowledgeBase() {
    const res = await fetch(`${API_BASE_URL}/knowledge-base`);
    if (!res.ok) throw new Error(`Failed to fetch knowledge base: HTTP ${res.status}`);
    return res.json();
  },

  async uploadBulk(formData) {
    const res = await fetch(`${API_BASE_URL}/tickets/bulk`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to upload CSV" }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }
};

window.SupportDeskAPI = API;
