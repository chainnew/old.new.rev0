import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface AppState {
  count: number
  theme: 'light' | 'dark'
  increment: () => void
  decrement: () => void
  toggleTheme: () => void
  setCount: (value: number) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      count: 0,
      theme: 'light',
      increment: () => set((state) => ({ count: state.count + 1 })),
      decrement: () => set((state) => ({ count: state.count - 1 })),
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
      setCount: (value) => set({ count: value }),
    }),
    {
      name: 'app-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ count: state.count, theme: state.theme }),
    }
  )
)