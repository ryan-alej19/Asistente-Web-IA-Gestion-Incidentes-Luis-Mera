import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ReportingPage from './pages/ReportingPage';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/report" element={<ReportingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
