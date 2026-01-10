import { dark } from '@clerk/themes';

export const clerkAppearance = {
    theme: [dark],
    variables: {
        colorPrimary: '#5f3dc4',
        colorBackground: '#181825',
        colorForeground: '#f3f3fa',
        colorInput: '#232336',
        colorInputForeground: '#f3f3fa',
        colorPrimaryForeground: '#fff',
        borderRadius: '12px',
        fontFamily: 'inherit',
    },
    layout: {
        socialButtonsPlacement: 'bottom',
        socialButtonsVariant: 'iconButton',
        shimmer: true,
        showOptionalFields: true,
    },
    elements: {
        card: {
            borderRadius: '12px',
            background: '#181825',
            border: '1px solid #232336',
            boxShadow: '0 4px 16px rgba(60, 0, 120, 0.10)',
        },
        formButtonPrimary: {
            background: '#5f3dc4',
            color: '#fff',
            fontWeight: 600,
            fontSize: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(95, 61, 196, 0.10)',
        },
        headerTitle: {
            color: '#f3f3fa',
            fontWeight: 700,
            fontSize: '1.15rem',
        },
        footer: {
            background: 'transparent',
            color: '#b4b4c2',
            fontSize: '0.95rem',
        },
        formFieldInput: {
            background: '#232336',
            color: '#f3f3fa',
            borderRadius: '8px',
            border: '1px solid #232336',
        },
        formFieldLabel: {
            color: '#b4b4c2',
            fontWeight: 500,
        },
        dividerText: {
            color: '#b4b4c2',
        },
        logoBox: {
            marginBottom: '1rem',
            width: '64px',
            height: '64px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
        },
    },
};
