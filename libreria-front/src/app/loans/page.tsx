// src/app/loans/page.tsx
import { getLoansList } from '@/lib/api';
import LoanList from '@/components/loans/LoanList';
import CreateLoanButton from '@/components/loans/CreateLoanButton';

export default async function LoansPage() {
  const loans = await getLoansList();

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Préstamos</h1>
        <CreateLoanButton />
      </div>
      <LoanList initialLoans={loans} />
    </div>
  );
}