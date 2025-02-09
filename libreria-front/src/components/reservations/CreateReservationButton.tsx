// src/components/reservations/CreateReservationButton.tsx
'use client';
import { useState, useEffect } from 'react';
import { createReservation, getUsers, getBooks } from '@/lib/api';
import { User, Book } from '@/types';

interface CreateReservationButtonProps {
  onReservationCreated: () => void;
}

interface FormData {
  book_id: number | '';
  user_id: number | '';
}

export default function CreateReservationButton({ onReservationCreated }: CreateReservationButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({
    book_id: '',
    user_id: ''
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        const [usersList, booksList] = await Promise.all([
          getUsers(),
          getBooks()
        ]);
        setUsers(usersList);
        setBooks(booksList.filter(book => book.status === 'borrowed'));
      } catch (err) {
        setError('Error al cargar los datos');
        console.error('Error loading data:', err);
      }
    };
    
    if (isModalOpen) {
      loadData();
    }
  }, [isModalOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (formData.book_id === '' || formData.user_id === '') {
        throw new Error('Selecciona un libro y un usuario');
      }

      await createReservation({
        book_id: Number(formData.book_id),
        user_id: Number(formData.user_id)
      });
      setIsModalOpen(false);
      onReservationCreated();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Error al crear la reservación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md"
      >
        Nueva Reservación
      </button>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Crear Nueva Reservación</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {error && (
              <div className="mb-4 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Usuario
                </label>
                <select
                  value={formData.user_id}
                  onChange={(e) => setFormData({...formData, user_id: e.target.value ? Number(e.target.value) : ''})}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                  required
                  disabled={loading}
                >
                  <option value="">Seleccionar usuario</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>
                      {user.first_name} {user.last_name} ({user.username})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Libro
                </label>
                <select
                  value={formData.book_id}
                  onChange={(e) => setFormData({...formData, book_id: e.target.value ? Number(e.target.value) : ''})}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                  required
                  disabled={loading}
                >
                  <option value="">Seleccionar libro</option>
                  {books.map(book => (
                    <option key={book.id} value={book.id}>
                      {book.title} - {book.author}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border rounded-md hover:bg-gray-100"
                  disabled={loading}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-blue-300"
                >
                  {loading ? 'Creando...' : 'Crear Reservación'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}