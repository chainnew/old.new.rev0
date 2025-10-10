"use client";

import { useAuth, useUser } from "@clerk/nextjs";
import { useEffect, useState } from "react";

interface ProtectedData {
  message: string;
  userId: string;
  token: string;
}

export function ProtectedComponent() {
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const [data, setData] = useState<ProtectedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      fetch("/api/protected", {
        headers: {
          Authorization: `Bearer ${user?.token}` || "",
        },
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error("Failed to fetch");
          }
          return res.json();
        })
        .then(setData)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [isLoaded, isSignedIn, user]);

  if (!isLoaded) return <p>Loading...</p>;
  if (!isSignedIn) return <p>Please sign in.</p>;

  if (loading) return <p>Loading protected data...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>Protected Content</h2>
      <p>{data?.message}</p>
      <p>User ID: {data?.userId}</p>
      {/* Do not display token in production UI */}
    </div>
  );
}