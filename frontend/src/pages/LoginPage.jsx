import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm.jsx';
import { useAuth } from '../hooks/useAuth.js';

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (email, password) => {
    setIsLoading(true);
    setErrorMessage('');
    const result = await login(email, password);
    if (result.success) {
      navigate('/plan-trip'); // Redirect to trip planning page on success
    } else {
      setErrorMessage(result.error || 'Login failed');
    }
    setIsLoading(false);
  };

  return (
    <AuthForm
      type="login"
      onSubmit={handleSubmit}
      isLoading={isLoading}
      errorMessage={errorMessage}
    />
  );
};

export default LoginPage;