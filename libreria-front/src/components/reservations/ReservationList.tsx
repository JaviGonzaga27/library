// src/components/reservations/ReservationList.tsx
'use client';
import { Reservation } from '@/types';
import ReservationCard from './ReservationCard';

interface ReservationListProps {
  reservations: Reservation[];
  onStatusChange: () => void;
}

export default function ReservationList({ reservations, onStatusChange }: ReservationListProps) {
  if (reservations.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No hay reservaciones registradas
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {reservations.map((reservation) => (
        <ReservationCard 
          key={reservation.id} 
          reservation={reservation}
          onStatusChange={onStatusChange}
        />
      ))}
    </div>
  );
}