
import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import { clerkAppearance } from '../clerkAppearance';
import { Container, Box } from '@mantine/core';

const SignUpPage: React.FC = () => {

    return (
        <Container size={420} my={80}>
            <Box>
                <SignUp
                    routing="path"
                    path="/sign-up"
                    signInUrl="/login"
                    fallbackRedirectUrl="/"
                    appearance={clerkAppearance}
                />
            </Box>
        </Container>
    );
};

export default SignUpPage;
