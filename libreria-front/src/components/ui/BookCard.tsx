// src/components/ui/BookCard.tsx
'use client';

import { Book } from '@/types';
import Link from 'next/link';

const statusTranslations = {
  'available': 'Disponible',
  'borrowed': 'Prestado',
  'lost': 'Perdido',
  'damaged': 'Dañado'
} as const;

const statusColors = {
  'available': 'bg-green-100 text-green-800',
  'borrowed': 'bg-yellow-100 text-yellow-800',
  'lost': 'bg-red-100 text-red-800',
  'damaged': 'bg-orange-100 text-orange-800'
} as const;

interface BookCardProps {
  book: Book;
}

export default function BookCard({ book }: BookCardProps) {
  return (
    <div className="border rounded-lg p-4 shadow hover:shadow-md transition">
      <h3 className="text-lg font-semibold">{book.title}</h3>
      <p className="text-gray-600">{book.author}</p>
      <div className="mt-2 flex justify-between items-center">
        <span className={`px-2 py-1 rounded-full text-sm ${statusColors[book.status]}`}>
          {statusTranslations[book.status]}
        </span>
        <Link 
          href={`/books/${book.id}`}
          className="text-blue-600 hover:text-blue-800"
        >
          Ver detalles
        </Link>
      </div>
    </div>
  );
}