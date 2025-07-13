// frontend/src/hooks/useAuth.js
'use client';

import { useContext } from 'react';
import { AuthContext } from '../contexts/auth-context-definition'; // <--- Import from the new file

export const useAuth = () => {
  return useContext(AuthContext);
};