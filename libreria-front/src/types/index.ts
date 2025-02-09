// src/types/index.ts
export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  }
  
  export interface Book {
    id: number;
    title: string;
    author: string;
    genre: string;
    code: string;
    status: 'available' | 'borrowed' | 'lost' | 'damaged';
    created_at: string;
    updated_at: string;
  }
  
  export interface Loan {
    id: number;
    book: Book;
    user: User;
    loan_date: string;
    due_date: string;
    returned_date: string | null;
    returned: boolean;
  }
  
  export interface Reservation {
    id: number;
    book: Book;
    user: User;
    reservation_date: string;
    active: boolean;
  }
  
  export interface Notification {
    id: number;
    subject: string;
    message: string;
    recipient: string;
    created_at: string;
    read: boolean;
  }

  // Auth types
  export interface LoginCredentials {
    username: string;
    password: string;
  }
  
  export interface AuthResponse {
    access: string;  // Django devuelve 'access' en lugar de 'token'
    refresh: string;
  }