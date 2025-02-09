// src/app/dashboard/page.tsx
'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function Dashboard() {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated && !localStorage.getItem('token')) {
      router.replace('/');
    }
    setIsLoading(false);
  }, [isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Barra de navegación */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-indigo-600">
                Sistema de Biblioteca
              </Link>
            </div>
            <div className="flex items-center">
              <button
                onClick={() => logout()}
                className="ml-4 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link 
              href="/dashboard/books" 
              className="p-6 border rounded-lg shadow hover:shadow-md transition bg-white"
            >
              <h2 className="text-xl font-semibold text-indigo-600">Libros</h2>
              <p className="text-gray-600">Gestionar catálogo de libros</p>
              <div className="mt-4 text-sm text-gray-500">
                Agregar, editar y eliminar libros
              </div>
            </Link>
            <Link 
              href="/dashboard/loans" 
              className="p-6 border rounded-lg shadow hover:shadow-md transition bg-white"
            >
              <h2 className="text-xl font-semibold text-indigo-600">Préstamos</h2>
              <p className="text-gray-600">Administrar préstamos activos</p>
              <div className="mt-4 text-sm text-gray-500">
                Registrar préstamos y devoluciones
              </div>
            </Link>
            <Link 
              href="/dashboard/reservations" 
              className="p-6 border rounded-lg shadow hover:shadow-md transition bg-white"
            >
              <h2 className="text-xl font-semibold text-indigo-600">Reservaciones</h2>
              <p className="text-gray-600">Gestionar reservas de libros</p>
              <div className="mt-4 text-sm text-gray-500">
                Ver y administrar reservaciones
              </div>
            </Link>
          </div>

          {/* Estadísticas */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700">Libros Totales</h3>
              <p className="text-2xl font-bold text-indigo-600">120</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700">Préstamos Activos</h3>
              <p className="text-2xl font-bold text-indigo-600">25</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700">Reservaciones</h3>
              <p className="text-2xl font-bold text-indigo-600">8</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700">Usuarios</h3>
              <p className="text-2xl font-bold text-indigo-600">50</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}