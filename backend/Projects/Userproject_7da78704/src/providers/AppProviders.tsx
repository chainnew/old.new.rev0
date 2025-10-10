import React, { PropsWithChildren } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient, QueryDevtools } from '@/lib/queryClient'; // Adjust alias if needed
import { Toaster } from '@/components/ui/toaster'; // Assume shadcn/ui or similar for toast

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <QueryDevtools />
      <Toaster />
    </QueryClientProvider>
  );
}