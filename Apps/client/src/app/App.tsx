import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SignIn, SignUp, useAuth } from '@clerk/clerk-react';
import { Container, Loader, Box } from '@mantine/core';
import Tools from '../pages/Tools';
import VideoDetail from '../pages/VideoDetail';
import Home from '../pages/Home';
import History from '../pages/History';
import ProtectedRoute from './ProtectedRoute';
import Layout from './Layout';
import OAuthCallback from './OAuthCallback';

const App = () => {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) {
    return (
      <Container size={420} my={80}>
        <Box style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
          <Loader size="lg" color="violet" />
        </Box>
      </Container>
    );
  }

  if (!isSignedIn) {
    return (
      <Router>
        <div className="centered-auth-container">
          <Container size={420}>
            <Routes>
              <Route path="/login" element={<SignIn />} />
              <Route path="/sign-up" element={<SignUp />} />
              <Route path="*" element={<SignIn />} />
            </Routes>
          </Container>
        </div>
      </Router>
    );
  }

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
          <Route path="/tools" element={<ProtectedRoute><Tools /></ProtectedRoute>} />
          <Route path="/video/:id" element={<ProtectedRoute><VideoDetail /></ProtectedRoute>} />
          <Route path="/oauth/success" element={<OAuthCallback />} />
          <Route path="/oauth/error" element={<OAuthCallback />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
