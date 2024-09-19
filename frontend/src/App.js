import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import FolderContent from './components/FolderContent';
import TestContent from './components/TestContent';


const App = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [initialPath, setInitialPath] = useState('/folder'); // Assurez-vous que ce chemin est correct

  const handleLogin = (path) => {
    setLoggedIn(true);
    setInitialPath(path || '/folder'); // Assurez-vous que `path` a une valeur correcte
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={!loggedIn ? <LoginForm onLogin={handleLogin} /> : <Navigate to={initialPath} replace />}
        />
        <Route path="/folder" element={<FolderContent />} />
        <Route path="/test" element={<TestContent />} />
      </Routes>
    </Router>
  );
};

export default App;
