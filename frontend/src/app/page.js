"use client"
import React, { useState, useEffect } from 'react';
import LandingPage from '@/components/LandingPage';
import SentimentApp from '@/components/SentimentApp';
import axios from 'axios';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // On component mount, check for a token and validate it
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      validateToken(token);
    }
  }, []);

  // Periodically refresh the token (every 5 minutes)
  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem('authToken');
      if (token) {
        refreshAuthToken(token);
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  // Validate the token by making a request to the backend
  const validateToken = async (token) => {
    try {
      await axios.get('https://your-backend-url.com/api/validate', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setIsAuthenticated(true);
    } catch (error) {
      handleLogout();
    }
  };

  // Refresh the token if needed by calling the backend refresh endpoint
  const refreshAuthToken = async (token) => {
    try {
      const response = await axios.get('https://your-backend-url.com/api/refresh', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token); // Update with new token
      } else {
        handleLogout(); // Logout if token refresh fails
      }
    } catch (error) {
      handleLogout();
    }
  };

  // Logout function clears the token and updates authentication state
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
  };

  // Authenticate user after login/signup
  const handleAuthenticate = (status) => {
    setIsAuthenticated(status);
  };

  return (
    <div className="App">
      {isAuthenticated ? (
        <SentimentApp onLogout={handleLogout} />
      ) : (
        <LandingPage onAuthenticate={handleAuthenticate} />
      )}
    </div>
  );
}

