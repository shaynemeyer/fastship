import { createContext, useEffect, useState } from 'react';
import { toast } from 'sonner';
import api from '~/lib/api';

interface AuthContextType {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  login: async () => {},
  logout: () => {},
});

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setToken(token);
      api.setSecurityData(token);
    }
  }, []);

  async function login(email: string, password: string) {
    try {
      const { data } = await api.seller.loginSeller({
        username: email,
        password,
      });

      if (data?.access_token) {
        setToken(data.access_token);
        api.setSecurityData(data.access_token);

        localStorage.setItem('token', data.access_token);

        console.log('Login successful');
      }
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
    }
  }

  async function logout() {
    api.seller.logoutSeller();
    setToken(null);
    api.setSecurityData(null);
    localStorage.removeItem('token');
  }

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthProvider, AuthContext, type AuthContextType };
