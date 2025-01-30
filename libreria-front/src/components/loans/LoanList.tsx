// src/components/loans/LoanList.tsx
'use client';

import { Loan } from '@/types';
import LoanCard from './LoanCard';

interface LoanListProps {
  initialLoans: Loan[];
}

export default function LoanList({ initialLoans }: LoanListProps) {
  return (
    <div className="grid grid-cols-1 gap-4">
      {initialLoans.map((loan) => (
        <LoanCard key={loan.id} loan={loan} />
      ))}
    </div>
  );
}