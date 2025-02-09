// src/lib/api.ts
import axios from 'axios';
import { Book, Loan, Reservation, User } from '@/types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Books
export const getBooks = async (): Promise<Book[]> => {
  const response = await api.get('/books/');
  return response.data;
};

export const searchBooks = async (type: string, query: string): Promise<Book[]> => {
  const response = await api.get(`/books/search/?type=${type}&query=${query}`);
  return response.data;
};

// Users
export const getUsers = async (): Promise<User[]> => {
  const response = await api.get('/users/');
  return response.data;
};

// Loans
export const getLoansList = async (): Promise<Loan[]> => {
  const response = await api.get('/loans/');
  return response.data;
};

export const createLoan = async (data: { book_id: number; user_id: number; due_date: string }): Promise<Loan> => {
  const response = await api.post('/loans/', data);
  return response.data;
};

export const returnBook = async (loanId: number): Promise<Loan> => {
  const response = await api.post(`/loans/${loanId}/return_book/`);
  return response.data;
};

// Reservations
export const getReservationsList = async (): Promise<Reservation[]> => {
  const response = await api.get('/reservations/');
  return response.data;
};

export const createReservation = async (data: { book_id: number; user_id: number }): Promise<Reservation> => {
  const response = await api.post('/reservations/', data);
  return response.data;
};