// src/components/reservations/ReservationCard.tsx
'use client';

import { Reservation } from '@/types';

interface ReservationCardProps {
  reservation: Reservation;
}

export default function ReservationCard({ reservation }: ReservationCardProps) {
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
        <div>
          <span className={`inline-block px-2 py-1 rounded-full text-sm ${
            reservation.active 
              ? 'bg-blue-100 text-blue-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {reservation.active ? 'Activa' : 'Finalizada'}
          </span>
        </div>
      </div>
    </div>
  );
}