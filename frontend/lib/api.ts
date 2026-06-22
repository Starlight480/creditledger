import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth
export const register = (data: { business_name: string; email: string; password: string; full_name: string; phone?: string }) =>
  api.post("/auth/register", data);

export const login = (data: { email: string; password: string }) =>
  api.post("/auth/login", data);

export const getMe = () => api.get("/auth/me");

// Business
export const getBusiness = () => api.get("/businesses/me");
export const updateBusiness = (data: { name?: string; phone?: string; address?: string }) =>
  api.put("/businesses/me", data);

// Debtors
export const getDebtors = (params?: { page?: number; page_size?: number; search?: string }) =>
  api.get("/debtors", { params });

export const createDebtor = (data: { name: string; phone?: string; email?: string; address?: string; notes?: string }) =>
  api.post("/debtors", data);

export const updateDebtor = (id: number, data: { name?: string; phone?: string; email?: string; address?: string; notes?: string }) =>
  api.put(`/debtors/${id}`, data);

export const deleteDebtor = (id: number) => api.delete(`/debtors/${id}`);

// Credits
export const getCredits = (params?: { page?: number; page_size?: number; status?: string; search?: string }) =>
  api.get("/credits", { params });

export const createCredit = (data: { debtor_id: number; amount: number; description?: string; due_date?: string }) =>
  api.post("/credits", data);

export const recordPayment = (creditId: number, data: { amount: number; method?: string; reference?: string; notes?: string }) =>
  api.post(`/credits/${creditId}/payments`, data);

export const getPayments = (creditId: number) => api.get(`/credits/${creditId}/payments`);

// Analytics
export const getSummary = () => api.get("/analytics/summary");
export const getTrends = (months?: number) => api.get("/analytics/trends", { params: { months } });
export const getOverdue = () => api.get("/analytics/overdue");
