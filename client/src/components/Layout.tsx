
import React from 'react';
import { useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  AppShell,
  Group,
  ActionIcon,
  useMantineColorScheme,
  Text,
  Container,
  Box,
  Anchor,
  Button,
  Stack,
  useMantineTheme
} from '@mantine/core';
import { UserButton, SignedIn, SignedOut, useAuth } from '@clerk/clerk-react';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const theme = useMantineTheme();
  const isDark = colorScheme === 'dark';
  const { isSignedIn, isLoaded } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      if (location.pathname === '/login' || location.pathname === '/sign-up') {
        navigate('/', { replace: true });
      }
    }
  }, [isSignedIn, isLoaded, navigate, location.pathname]);

  return (
    <AppShell
      header={{ height: 80 }}
      padding="md"
      styles={{
        main: {
          backgroundColor: isDark ? theme.colors.dark[8] : theme.colors.gray[0],
          minHeight: '100vh',
          color: isDark ? theme.colors.gray[2] : theme.colors.dark[7],
        },
      }}
    >
      <AppShell.Header
        withBorder={false}
        style={{
          backdropFilter: 'blur(16px)',
          backgroundColor: isDark
            ? 'rgba(18, 18, 28, 0.92)'
            : 'rgba(255, 255, 255, 0.92)',
          borderBottom: `1px solid ${isDark ? theme.colors.dark[5] : theme.colors.gray[2]}`
        }}
      >
        <Container size="lg" h="100%">
          <Group h="100%" justify="space-between">
            <Group gap={40}>
              <Box
                component={Link}
                to="/"
                style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '12px' }}
              >
                <Box
                  bg="gradient"
                  style={{
                    background: isDark
                      ? `linear-gradient(135deg, ${theme.colors.indigo[6]}, ${theme.colors.violet[6]})`
                      : `linear-gradient(135deg, ${theme.colors.indigo[1]}, ${theme.colors.violet[0]})`,
                    padding: '8px',
                    borderRadius: '12px',
                    display: 'flex',
                    color: isDark ? theme.white : theme.colors.indigo[7],
                    boxShadow: isDark
                      ? '0 4px 12px rgba(99, 102, 241, 0.3)'
                      : '0 4px 12px rgba(99, 102, 241, 0.10)'
                  }}
                >
                  <i className="fas fa-brain"></i>
                </Box>
                <Text
                  size="xl"
                  fw={900}
                  style={{
                    letterSpacing: '-0.8px',
                    color: isDark ? theme.colors.indigo[2] : theme.colors.indigo[8],
                    textShadow: isDark ? '0 1px 2px rgba(0,0,0,0.25)' : '0 1px 2px rgba(99,102,241,0.08)'
                  }}
                  variant={isDark ? 'gradient' : undefined}
                  gradient={isDark ? { from: 'indigo.7', to: 'violet.7' } : undefined}
                >
                  VidSage
                </Text>
              </Box>

              <Group gap="xl" visibleFrom="sm">
                <Anchor
                  component={Link}
                  to="/"
                  c={location.pathname === '/' ? 'indigo' : 'gray.6'}
                  fw={location.pathname === '/' ? 800 : 600}
                  size="sm"
                  underline="never"
                >
                  Home
                </Anchor>
                <SignedIn>
                  <Anchor
                    component={Link}
                    to="/history"
                    c={location.pathname === '/history' ? 'indigo' : 'gray.6'}
                    fw={location.pathname === '/history' ? 800 : 600}
                    size="sm"
                    underline="never"
                  >
                    History
                  </Anchor>
                  <Anchor
                    component={Link}
                    to="/tools"
                    c={location.pathname === '/tools' ? 'indigo' : 'gray.6'}
                    fw={location.pathname === '/tools' ? 800 : 600}
                    size="sm"
                    underline="never"
                  >
                    Integrations
                  </Anchor>
                </SignedIn>
              </Group>
            </Group>

            <Group gap="md">
              <ActionIcon
                onClick={() => toggleColorScheme()}
                variant="subtle"
                size="lg"
                color="gray"
                radius="xl"
              >
                <i className={`fas ${isDark ? 'fa-sun' : 'fa-moon'}`}></i>
              </ActionIcon>

              <SignedIn>
                <UserButton
                  appearance={{
                    elements: {
                      avatarBox: "w-10 h-10"
                    }
                  }}
                />
              </SignedIn>

              <SignedOut>
                <Button component={Link} to="/login" variant="filled" color="indigo" radius="xl" size="sm" px={20}>
                  Get Started
                </Button>
              </SignedOut>
            </Group>
          </Group>
        </Container>
      </AppShell.Header>

      <AppShell.Main>
        <Container size="xl" p="xl">
          {children}
        </Container>

        <Box
          component="footer"
          py={60}
          mt={80}
          style={{
            borderTop: `1px solid ${isDark ? theme.colors.dark[5] : theme.colors.gray[2]}`,
            background: isDark ? theme.colors.dark[7] : theme.colors.gray[0],
            color: isDark ? theme.colors.gray[2] : theme.colors.dark[7],
          }}
        >
          <Container size="xl">
            <Group justify="space-between">
              <Stack gap={5}>
                <Text
                  fw={900}
                  size="lg"
                  variant="gradient"
                  gradient={{ from: 'indigo', to: 'violet' }}
                  style={{ color: isDark ? theme.colors.indigo[2] : theme.colors.indigo[8] }}
                >
                  VidSage AI
                </Text>
                <Text c={isDark ? 'gray.4' : 'gray.7'} size="xs">Deciphering the digital stream, one frame at a time.</Text>
                <Text c={isDark ? 'gray.4' : 'gray.7'} size="xs" mt={8}>
                  Developed by{' '}
                  <Anchor href="https://github.com/Thiwanka-Sandakalum" target="_blank" fw={700} c="indigo">
                    Thiwanka Sandakalum
                  </Anchor>
                </Text>
                <Group gap={8} mt={4}>
                  <Anchor href="https://github.com/Thiwanka-Sandakalum/VidSage" target="_blank" size="xs" c={isDark ? 'gray.3' : 'gray.7'}>
                    <i className="fab fa-github" style={{ marginRight: 4 }}></i> GitHub Repo
                  </Anchor>
                  <Anchor href="https://www.linkedin.com/in/thiwanka-sandakalum/" target="_blank" size="xs" c={isDark ? 'gray.3' : 'gray.7'}>
                    <i className="fab fa-linkedin" style={{ marginRight: 4 }}></i> LinkedIn
                  </Anchor>
                  <Anchor href="https://thiwanka-sandakalum.github.io/personal-website/" target="_blank" size="xs" c={isDark ? 'gray.3' : 'gray.7'}>
                    <i className="fas fa-globe" style={{ marginRight: 4 }}></i> Website
                  </Anchor>
                  <Anchor href="mailto:thiwanka2002sandakalum@gmail.com" target="_blank" size="xs" c={isDark ? 'gray.3' : 'gray.7'}>
                    <i className="fas fa-envelope" style={{ marginRight: 4 }}></i> Contact
                  </Anchor>
                </Group>
              </Stack>
            </Group>
          </Container>
        </Box>
      </AppShell.Main>
    </AppShell>
  );
};

export default Layout;
