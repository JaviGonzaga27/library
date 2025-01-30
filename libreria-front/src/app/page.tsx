// src/app/page.tsx
import Link from 'next/link';

export default function Home() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Sistema de Biblioteca</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link 
          href="/books" 
          className="p-6 border rounded-lg shadow hover:shadow-md transition"
        >
          <h2 className="text-xl font-semibold">Libros</h2>
          <p className="text-gray-600">Gestionar catálogo</p>
        </Link>
        <Link 
          href="/loans" 
          className="p-6 border rounded-lg shadow hover:shadow-md transition"
        >
          <h2 className="text-xl font-semibold">Préstamos</h2>
          <p className="text-gray-600">Administrar préstamos</p>
        </Link>
        <Link 
          href="/reservations" 
          className="p-6 border rounded-lg shadow hover:shadow-md transition"
        >
          <h2 className="text-xl font-semibold">Reservaciones</h2>
          <p className="text-gray-600">Gestionar reservas</p>
        </Link>
      </div>
    </main>
  );
}