import { useQuery } from '@tanstack/react-query';
import { useUserStore } from '../store/userStore';

interface UserData {
  id: string;
  name: string;
  email: string;
}

async function fetchUser(userId: string): Promise<UserData> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
}

export function useUser(userId?: string) {
  const { user, isAuthenticated } = useUserStore();

  return useQuery({
    queryKey: ['user', userId || user?.id],
    queryFn: () => fetchUser(userId || user!.id),
    enabled: !!userId || isAuthenticated,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}