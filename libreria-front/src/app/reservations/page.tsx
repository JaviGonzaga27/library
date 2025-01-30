// src/app/reservations/page.tsx
import { getReservationsList } from '@/lib/api';
import ReservationList from '@/components/reservations/ReservationList';
import CreateReservationButton from '@/components/reservations/CreateReservationButton';

export default async function ReservationsPage() {
  const reservations = await getReservationsList();

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Reservaciones</h1>
        <CreateReservationButton />
      </div>
      <ReservationList initialReservations={reservations} />
    </div>
  );
}