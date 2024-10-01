import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import Menuprincipal from './components/Menuprincipal'; // Import the new Menuprincipal component
import 'bootstrap/dist/css/bootstrap.min.css';

const App = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [initialPath, setInitialPath] = useState('/menuprincipal'); // Update path

  const handleLogin = (path) => {
    setLoggedIn(true);
    setInitialPath(path || '/menuprincipal'); // Update initialPath to Menuprincipal
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={!loggedIn ? <LoginForm onLogin={handleLogin} /> : <Navigate to={initialPath} replace />}
        />
        <Route path="/menuprincipal" element={<Menuprincipal />} />
      </Routes>
    </Router>
  );
};

export default App;
