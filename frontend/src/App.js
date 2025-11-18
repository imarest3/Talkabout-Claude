import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import { PrivateRoute, PublicRoute } from './components/PrivateRoute';
import Navbar from './components/Navbar';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Activities from './pages/Activities';
import ActivityDetail from './pages/ActivityDetail';
import MyActivities from './pages/MyActivities';
import MyEnrollments from './pages/MyEnrollments';
import Statistics from './pages/Statistics';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
            <Navbar />
            <Routes>
              {/* Public Routes */}
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                }
              />
              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                }
              />

              {/* Private Routes */}
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <Home />
                  </PrivateRoute>
                }
              />
              <Route
                path="/activities"
                element={
                  <PrivateRoute>
                    <Activities />
                  </PrivateRoute>
                }
              />
              <Route
                path="/activities/:id"
                element={
                  <PrivateRoute>
                    <ActivityDetail />
                  </PrivateRoute>
                }
              />
              <Route
                path="/my-activities"
                element={
                  <PrivateRoute requiredRole="teacher">
                    <MyActivities />
                  </PrivateRoute>
                }
              />
              <Route
                path="/my-enrollments"
                element={
                  <PrivateRoute>
                    <MyEnrollments />
                  </PrivateRoute>
                }
              />
              <Route
                path="/statistics"
                element={
                  <PrivateRoute>
                    <Statistics />
                  </PrivateRoute>
                }
              />
            </Routes>
          </Box>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
