import { useAppStore } from '@/stores/useAppStore'; // Adjust alias if needed

function App() {
  const { theme, toggleTheme } = useAppStore();

  return (
    <div className={theme}>
      <h1>UserProject</h1>
      <button onClick={toggleTheme}>Toggle Theme</button>
      {/* Your app content */}
    </div>
  );
}

export default App;