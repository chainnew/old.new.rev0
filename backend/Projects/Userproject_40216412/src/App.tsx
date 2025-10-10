import { QueryProvider } from './providers/QueryProvider';
import { useUserStore } from './store/userStore';
import { useUser } from './hooks/useUser';
import { useEffect } from 'react';

function App() {
  const { user, isAuthenticated, setUser, logout } = useUserStore();
  const { data: userData, isLoading, error } = useUser();

  useEffect(() => {
    if (userData && !user) {
      setUser(userData);
    }
  }, [userData, user, setUser]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <QueryProvider>
      <div className="app">
        {isAuthenticated ? (
          <div>
            <h1>Welcome, {user?.name}</h1>
            <button onClick={logout}>Logout</button>
          </div>
        ) : (
          <div>
            <h1>Please log in</h1>
            {/* Login form or component here */}
          </div>
        )}
      </div>
    </QueryProvider>
  );
}

export default App;