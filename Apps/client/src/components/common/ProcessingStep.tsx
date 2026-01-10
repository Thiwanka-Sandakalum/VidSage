import React from 'react';
import { Text, Box, Loader, ThemeIcon, rem, useMantineColorScheme, useMantineTheme, Group } from '@mantine/core';

interface StepProps {
    label: string;
    state: 'pending' | 'active' | 'completed';
}

const ProcessingStep: React.FC<StepProps> = ({ label, state }) => {
    const theme = useMantineTheme();
    const { colorScheme } = useMantineColorScheme();
    const isDark = colorScheme === 'dark';

    const getIcon = () => {
        switch (state) {
            case 'completed':
                return (
                    <ThemeIcon color="green" variant={isDark ? 'filled' : 'light'} radius="xl" size="md">
                        <i className="fas fa-check text-[10px]"></i>
                    </ThemeIcon>
                );
            case 'active':
                return (
                    <Box style={{ position: 'relative', width: rem(28), height: rem(28), display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Loader size={rem(22)} stroke="2" color={isDark ? 'grape' : 'indigo'} />
                    </Box>
                );
            default:
                return (
                    <Box
                        style={{
                            width: rem(24),
                            height: rem(24),
                            borderRadius: '50%',
                            border: `2px solid ${isDark ? theme.colors.dark[4] : theme.colors.gray[2]}`,
                            margin: '2px',
                            background: isDark ? theme.colors.dark[6] : theme.white
                        }}
                    />
                );
        }
    };

    return (
        <Group gap="md" py={12}>
            <Box w={32} display="flex" style={{ justifyContent: 'center' }}>
                {getIcon()}
            </Box>
            <Text
                size="md"
                fw={state === 'active' ? 700 : 500}
                c={state === 'pending' ? (isDark ? 'gray.5' : 'dimmed') : state === 'active' ? (isDark ? 'grape.3' : 'indigo.6') : (isDark ? 'gray.2' : 'dark.7')}
                style={{ transition: 'all 0.3s ease' }}
            >
                {label}
            </Text>
        </Group>
    );
};

export default ProcessingStep;