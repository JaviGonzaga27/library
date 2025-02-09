// src/app/dashboard/loans/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { getLoansList } from '@/lib/api';
import { Loan } from '@/types';
import LoanList from '@/components/loans/LoanList';
import CreateLoanButton from '@/components/loans/CreateLoanButton';

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLoans = async () => {
    try {
      setIsLoading(true);
      const data = await getLoansList();
      setLoans(data);
      setError(null);
    } catch (error) {
      setError('Error al cargar los préstamos');
      console.error('Error fetching loans:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans();
  }, []);

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Préstamos</h1>
        <CreateLoanButton onLoanCreated={fetchLoans} />
      </div>
      {isLoading ? (
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <LoanList loans={loans} onStatusChange={fetchLoans} />
      )}
    </div>
  );
}