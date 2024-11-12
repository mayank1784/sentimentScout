"use client"
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function LandingPage({ onAuthenticate }) {  // Receive onAuthenticate prop to update App's state
  const [activeTab, setActiveTab] = useState('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    userName: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Handle input change
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  useEffect(() => {
    // Demo data to send in the POST request
    const demoData = {
      username: 'new_user', // New username
      email: 'user@example.com', // New email
      password: 'securepassword123', // New password
    };

    const registerUser = async () => {
      try {
        // Make the POST request to register the user
        const response = await axios.post(`${process.env.BACKEND_BASE_URL}/register`, demoData);

        // Handle success
        setStatus({ type: 'success', message: response.data.message });
      } catch (error) {
        // Handle error responses
        if (error.response) {
          // If error response exists
          if (error.response.status === 409) {
            // Username or email already exists
            setStatus({ type: 'error', message: error.response.data.message });
          } else if (error.response.status === 400) {
            console.log(error)
          }
        } else {
          // Handle other errors (like no response)
          setStatus({ type: 'error', message: 'Network error or server down' });
        }
      }
    };

    // Call the function to register the user
    registerUser();
  }, []); // Empty dependency array to run the effect once


  // Basic email validation using regex
  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  // Handle form submission for login and Register
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Form validation
    if (!formData.email || !formData.password) {
      setError('All fields are required');
      setLoading(false);
      return;
    }
    if (!isValidEmail(formData.email)) {
      setError('Invalid email format');
      setLoading(false);
      return;
    }
    if (activeTab === 'Register' && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (activeTab === 'Register' && !(validateUsername(formData.userName))) {
      setError('Username is not valid');
      setLoading(false);
      return;
    }

    function validateUsername(username) {
      const regex = /^[a-zA-Z0-9_-]{3,20}$/;
      return regex.test(username);
    }

    try {
      // Define API endpoint based on activeTab
      const apiUrl = activeTab === 'login' ? `${process.env.BACKEND_BASE_URL}/login` : `${process.env.BACKEND_BASE_URL}/register`;
      console.log('activeTab:', activeTab, apiUrl);
      const response = await axios.post(apiUrl, {
        email: formData.email,
        password: formData.password,
        username: formData.userName,
      });


      // // Handle successful authentication
      // if (response.data.token) {
      //   localStorage.setItem('authToken', response.data.token);  // Store token locally
      //   onAuthenticate(true);  // Update App's isAuthenticated state
      // }
      console.log(JSON.stringify(response,null,2));

    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Incorrect email or password');
      } else if (err.response && err.response.status === 400) {
        setError('Account already exists or invalid Register details');
      } else {
        setError('Network error. Please try again later.');
      }
    } finally {
      setLoading(false);
    } 
};
 

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white shadow-md rounded-lg max-w-md w-full p-8">
        <h1 className="text-2xl font-bold text-center text-blue-600 mb-6">Welcome to Sentiment Scout</h1>

        {/* Tabs for Login and Register */}
        <div className="flex justify-center mb-4">
          <button
            onClick={() => setActiveTab('login')}
            className={`px-4 py-2 text-sm font-semibold ${activeTab === 'login' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Login
          </button>
          <button
            onClick={() => setActiveTab('Register')}
            className={`px-4 py-2 text-sm font-semibold ${activeTab === 'Register' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Register
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-gray-700"
              required
            />
          </div>

          {/* Confirm Password Field for Register */}
          {activeTab === 'Register' && (
            <div className="mb-4">
              <label className="block text-gray-700">Username</label>
              <input
                type="text"
                name="userName"
                value={formData.userName}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-gray-700"
                required
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <p className="text-red-500 text-sm mb-4">{error}</p>
          )}

          <div className="mb-4">
            <label className="block text-gray-700">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-gray-700"
              required
            />
          </div>

          {/* Confirm Password Field for Register */}
          {activeTab === 'Register' && (
            <div className="mb-4">
              <label className="block text-gray-700">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-gray-700"
                required
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <p className="text-red-500 text-sm mb-4">{error}</p>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-md transition duration-200"
          >
            {loading ? (activeTab === 'login' ? 'Logging in...' : 'Signing up...') : activeTab === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        {/* Divider */}
        <div className="mt-6 border-t border-gray-300 pt-4 text-center text-sm text-gray-600">
          {activeTab === 'login' ? (
            <>Don't have an account? <button onClick={() => setActiveTab('Register')} className="text-blue-600 font-semibold">Sign up</button></>
          ) : (
            <>Already have an account? <button onClick={() => setActiveTab('login')} className="text-blue-600 font-semibold">Login</button></>
          )}
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
