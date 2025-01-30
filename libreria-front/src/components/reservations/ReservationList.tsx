// src/components/reservations/ReservationList.tsx
'use client';

import { Reservation } from '@/types';
import ReservationCard from './ReservationCard';

interface ReservationListProps {
  initialReservations: Reservation[];
}

export default function ReservationList({ initialReservations }: ReservationListProps) {
  return (
    <div className="grid grid-cols-1 gap-4">
      {initialReservations.map((reservation) => (
        <ReservationCard key={reservation.id} reservation={reservation} />
      ))}
    </div>
  );
}