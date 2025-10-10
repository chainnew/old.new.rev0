export function DashboardContent() {
  // Simulate fetching user data; in production, use server components or API routes
  const userStats = {
    totalUsers: 150,
    activeSessions: 45,
    lastLogin: '2023-10-01',
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">Total Users</h3>
        <p className="text-2xl">{userStats.totalUsers}</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">Active Sessions</h3>
        <p className="text-2xl">{userStats.activeSessions}</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">Last Login</h3>
        <p className="text-2xl">{userStats.lastLogin}</p>
      </div>
    </div>
  );
}