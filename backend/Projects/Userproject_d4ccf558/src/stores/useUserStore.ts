import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface UserState {
  user: {
    id: string
    name: string
    email: string
  } | null
  isAuthenticated: boolean
  login: (userData: { id: string; name: string; email: string }) => void
  logout: () => void
  setAuthenticated: (auth: boolean) => void
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        isAuthenticated: false,
        login: (userData) => set({ user: userData, isAuthenticated: true }),
        logout: () => set({ user: null, isAuthenticated: false }),
        setAuthenticated: (auth) => set({ isAuthenticated: auth }),
      }),
      {
        name: 'user-storage',
        partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
      },
    ),
    { name: 'UserStore' },
  ),
)