import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm.jsx';
import { useAuth } from '../hooks/useAuth.js';

const RegisterPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (email, password, fullName) => {
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    const result = await register(email, password, fullName);
    if (result.success) {
      setSuccessMessage(result.message || 'Registration successful! You can now log in.');
      // Optionally redirect to login page after a short delay
      setTimeout(() => navigate('/login'), 2000);
    } else {
      setErrorMessage(result.error || 'Registration failed');
    }
    setIsLoading(false);
  };

  return (
    <div>
      {successMessage && <p className="success-message" style={{textAlign: 'center'}}>{successMessage}</p>}
      <AuthForm
        type="register"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        errorMessage={errorMessage}
      />
    </div>
  );
};

export default RegisterPage;