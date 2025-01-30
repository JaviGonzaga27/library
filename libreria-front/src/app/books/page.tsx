// src/app/books/page.tsx
import { getBooks } from '@/lib/api';
import BookCard from '@/components/ui/BookCard';
import { Book } from '@/types';

export default async function BooksPage() {
  const books = await getBooks();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Catálogo de Libros</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {books.map((book: Book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>
    </div>
  );
}