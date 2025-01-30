// src/components/loans/LoanCard.tsx
'use client';

import { Loan } from '@/types';
import { returnBook } from '@/lib/api';
import { useState } from 'react';

interface LoanCardProps {
 loan: Loan;
 onStatusChange?: () => void;
}

export default function LoanCard({ loan, onStatusChange }: LoanCardProps) {
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState<string | null>(null);

 const isOverdue = new Date(loan.due_date) < new Date() && !loan.returned;

 const handleReturn = async () => {
   setLoading(true);
   setError(null);
   try {
     await returnBook(loan.id);
     if (onStatusChange) {
       onStatusChange();
     } else {
       window.location.reload();
     }
   } catch (err) {
     setError('Error al devolver el libro');
     console.error('Error returning book:', err);
   } finally {
     setLoading(false);
   }
 };

 return (
   <div className="border rounded-lg p-4 shadow hover:shadow-md transition">
     <div className="flex justify-between items-start">
       <div>
         <h3 className="text-lg font-semibold">{loan.book.title}</h3>
         <p className="text-gray-600">
           Usuario: {loan.user.first_name} {loan.user.last_name}
         </p>
         <div className="mt-2 space-y-1">
           <p className="text-sm text-gray-500">
             Fecha préstamo: {new Date(loan.loan_date).toLocaleDateString('es-ES')}
           </p>
           <p className="text-sm text-gray-500">
             Fecha devolución: {new Date(loan.due_date).toLocaleDateString('es-ES')}
           </p>
           {loan.returned && loan.returned_date && (
             <p className="text-sm text-gray-500">
               Devuelto el: {new Date(loan.returned_date).toLocaleDateString('es-ES')}
             </p>
           )}
         </div>
       </div>
       <div className="space-y-2">
         <span className={`inline-block px-2 py-1 rounded-full text-sm ${
           loan.returned 
             ? 'bg-green-100 text-green-800' 
             : isOverdue
               ? 'bg-red-100 text-red-800'
               : 'bg-yellow-100 text-yellow-800'
         }`}>
           {loan.returned 
             ? 'Devuelto' 
             : isOverdue
               ? 'Vencido'
               : 'En préstamo'
           }
         </span>
         {!loan.returned && (
           <button
             onClick={handleReturn}
             disabled={loading}
             className="block w-full px-3 py-1 text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400"
           >
             {loading ? 'Procesando...' : 'Marcar como devuelto'}
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