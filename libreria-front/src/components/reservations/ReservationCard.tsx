// src/components/reservations/ReservationCard.tsx
'use client';
import { useState } from 'react';
import { Reservation } from '@/types';
import { cancelReservation } from '@/lib/api';

interface ReservationCardProps {
  reservation: Reservation;
  onStatusChange: () => void;
}

export default function ReservationCard({ reservation, onStatusChange }: ReservationCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCancel = async () => {
    setLoading(true);
    setError(null);
    try {
      await cancelReservation(reservation.id);
      onStatusChange();
    } catch (err) {
      setError('Error al cancelar la reservación');
      console.error('Error canceling reservation:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 shadow hover:shadow-md transition">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold">{reservation.book.title}</h3>
          <p className="text-gray-600">
            Usuario: {reservation.user.first_name} {reservation.user.last_name}
          </p>
          <div className="mt-2">
            <p className="text-sm text-gray-500">
              Fecha reserva: {new Date(reservation.reservation_date).toLocaleDateString('es-ES')}
            </p>
          </div>
        </div>
        <div className="space-y-2">
          <span className={`inline-block px-2 py-1 rounded-full text-sm ${
            reservation.active 
              ? 'bg-blue-100 text-blue-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {reservation.active ? 'Activa' : 'Finalizada'}
          </span>
          {reservation.active && (
            <button
              onClick={handleCancel}
              disabled={loading}
              className="block w-full px-3 py-1 text-sm text-red-600 hover:text-red-800 disabled:text-gray-400"
            >
              {loading ? 'Procesando...' : 'Cancelar reservación'}
            </button>
          )}
        </div>
      </div>
      {error && (
        <div className="mt-2 p-2 text-sm text-red-600 bg-red-50 rounded">
          {error}
        </div>
      )}
    </div>
  );
}