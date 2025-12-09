import { Dashboard } from './components/Dashboard';
import { Toaster } from 'react-hot-toast';
import './App.css';

function App() {
  return (
    <>
      <Dashboard />
      <Toaster
        position="top-right"
        reverseOrder={false}
        gutter={8}
        toastOptions={{
          // 기본 옵션
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          // 성공 토스트
          success: {
            duration: 4000,
            iconTheme: {
              primary: '#22c55e',
              secondary: '#fff',
            },
          },
          // 에러 토스트
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </>
  );
}

export default App;
