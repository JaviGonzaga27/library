// src/app/dashboard/reservations/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { getReservationsList } from '@/lib/api';
import { Reservation } from '@/types';
import ReservationList from '@/components/reservations/ReservationList';
import CreateReservationButton from '@/components/reservations/CreateReservationButton';

export default function ReservationsPage() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReservations = async () => {
    try {
      setIsLoading(true);
      const data = await getReservationsList();
      setReservations(data);
      setError(null);
    } catch (error) {
      setError('Error al cargar las reservaciones');
      console.error('Error fetching reservations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReservations();
  }, []);

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Reservaciones</h1>
        <CreateReservationButton onReservationCreated={fetchReservations} />
      </div>
      {isLoading ? (
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <ReservationList reservations={reservations} onStatusChange={fetchReservations} />
      )}
    </div>
  );
}