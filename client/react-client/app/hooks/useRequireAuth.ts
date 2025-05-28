import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../utils/auth';

interface UseRequireAuthOptions {
  redirectTo?: string;
  onUnauthenticated?: () => void;
}

export const useRequireAuth = (options: UseRequireAuthOptions = {}) => {
  const router = useRouter();
  const {
    redirectTo = '/login',
    onUnauthenticated
  } = options;

  useEffect(() => {
    // Check if we're in the browser
    if (typeof window === 'undefined') return;

    const checkAuth = () => {
      if (!isAuthenticated()) {
        // Call the onUnauthenticated callback if provided
        if (onUnauthenticated) {
          onUnauthenticated();
        }
        // Redirect to login page
        router.push(redirectTo);
      }
    };

    checkAuth();
  }, [router, redirectTo, onUnauthenticated]);

  return {
    isAuthenticated: isAuthenticated()
  };
};
