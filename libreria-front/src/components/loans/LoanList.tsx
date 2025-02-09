// src/components/loans/LoanList.tsx
'use client';
import { Loan } from '@/types';
import LoanCard from './LoanCard';

interface LoanListProps {
  loans: Loan[];
  onStatusChange: () => void;
}

export default function LoanList({ loans, onStatusChange }: LoanListProps) {
  if (loans.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No hay préstamos registrados
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {loans.map((loan) => (
        <LoanCard 
          key={loan.id} 
          loan={loan} 
          onStatusChange={onStatusChange}
        />
      ))}
    </div>
  );
}