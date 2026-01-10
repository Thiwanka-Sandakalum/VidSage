
import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { clerkAppearance } from '../clerkAppearance';
import { Container, Box } from '@mantine/core';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container size={420} my={80}>
      <Box>
        <SignIn
          routing="path"
          path="/login"
          signUpUrl="/sign-up"
          fallbackRedirectUrl="/"
          appearance={clerkAppearance}
        />
      </Box>
    </Container>
  );
};

export default Login;