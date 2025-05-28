'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import LoginScreen from '../components/auth/LoginScreen';
import { isAuthenticated } from '../utils/auth';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is already authenticated
    if (isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  // Don't render the login form if user is already authenticated
  if (isAuthenticated()) {
    return null; // or a loading spinner
  }

  return <LoginScreen />;
}
