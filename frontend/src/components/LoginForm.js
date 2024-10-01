import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  console.log("Environment Variables:", process.env);

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    console.log(process.env.REACT_APP_IP_SERV);  // Devrait afficher l'URL
  
    try {
      const response = await fetch(`${process.env.REACT_APP_IP_SERV}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
  
      const data = await response.json();
      localStorage.setItem('token', data.token);
      setMessage('Login successful');
  
      if (data.role === 'test') {
        navigate('/test');
      } else if (data.role === 'user') {
        navigate('/menuprincipal');
      } else {
        setMessage('Role not recognized');
      }
    } catch (error) {
      setMessage(error.message);
    }
  };
  

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Login</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Login;
