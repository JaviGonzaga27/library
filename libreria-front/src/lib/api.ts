// src/lib/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';
import { Book, Loan, Reservation, User, LoginCredentials, AuthResponse } from '@/types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Función auxiliar para obtener headers de autenticación
const getAuthHeader = () => {
  const token = Cookies.get('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Books
export const getBooks = async (): Promise<Book[]> => {
  try {
    const token = Cookies.get('token');
    if (!token) {
      throw new Error('No authentication token');
    }

    const response = await api.get('/books/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching books:', error);
    throw error;
  }
};

export const searchBooks = async (type: string, query: string): Promise<Book[]> => {
  try {
    const response = await api.get(`/books/search/?type=${type}&query=${query}`, {
      headers: getAuthHeader()
    });
    return response.data;
  } catch (error) {
    console.error('Error searching books:', error);
    return [];
  }
};

// Users
export const getUsers = async (): Promise<User[]> => {
  try {
    const response = await api.get('/users/', {
      headers: getAuthHeader()
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    return [];
  }
};

// Loans
export const getLoansList = async (): Promise<Loan[]> => {
  try {
    const response = await api.get('/loans/', {
      headers: getAuthHeader()
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching loans:', error);
    return [];
  }
};

export const createLoan = async (data: { book_id: number; user_id: number; due_date: string }): Promise<Loan> => {
  const response = await api.post('/loans/', data, {
    headers: getAuthHeader()
  });
  return response.data;
};

export const returnBook = async (loanId: number): Promise<Loan> => {
  const response = await api.post(`/loans/${loanId}/return_book/`, {}, {
    headers: getAuthHeader()
  });
  return response.data;
};

// Reservations
export const getReservationsList = async (): Promise<Reservation[]> => {
  try {
    const response = await api.get('/reservations/', {
      headers: getAuthHeader()
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching reservations:', error);
    return [];
  }
};

export const createReservation = async (data: { book_id: number; user_id: number }): Promise<Reservation> => {
  const response = await api.post('/reservations/', data, {
    headers: getAuthHeader()
  });
  return response.data;
};

export const cancelReservation = async (reservationId: number): Promise<void> => {
  try {
    await api.post(`/reservations/${reservationId}/cancel/`, {}, {
      headers: getAuthHeader()
    });
  } catch (error) {
    console.error('Error canceling reservation:', error);
    throw error;
  }
};

// Auth endpoints
// Corregir la ruta del endpoint de login
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  try {
    const response = await api.post('/token/', credentials);
    
    if (response.data.access) {
      Cookies.set('token', response.data.access, { expires: 7 });
      Cookies.set('refresh_token', response.data.refresh, { expires: 30 });
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
      return response.data;
    }
    throw new Error('No access token received');
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const refreshToken = async (): Promise<AuthResponse> => {
  try {
    const refresh = Cookies.get('refresh_token');
    if (!refresh) {
      throw new Error('No refresh token available');
    }

    const response = await api.post('/token/refresh/', { refresh });
    
    if (response.data.access) {
      Cookies.set('token', response.data.access, { expires: 7 });
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
      return response.data;
    }
    throw new Error('No access token received from refresh');
  } catch (error) {
    console.error('Token refresh error:', error);
    throw error;
  }
};

export const logout = () => {
  // Eliminar cookies
  Cookies.remove('token');
  Cookies.remove('refresh_token');
  
  // Limpiar headers
  delete api.defaults.headers.common['Authorization'];
};

// Interceptor para manejar tokens expirados
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await refreshToken();
        return api(originalRequest);
      } catch (refreshError) {
        logout();
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Interceptor para añadir el token a todas las peticiones
api.interceptors.request.use((config) => {
  const token = Cookies.get('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;