import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { notifications } from '@mantine/notifications';
import Tools from '../../pages/Tools';

const OAuthCallback = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const error = searchParams.get('error');

    useEffect(() => {
        if (error) {
            setStatus('error');
            notifications.show({
                title: 'OAuth Error',
                message: error === 'access_denied'
                    ? 'You denied access to your Google account'
                    : 'Failed to connect to Google',
                color: 'red',
            });
        } else {
            // Success - redirect to tools page
            setStatus('success');
            notifications.show({
                title: 'Connected!',
                message: 'Your Google account has been connected successfully',
                color: 'green',
            });

            setTimeout(() => {
                navigate('/tools');
            }, 2000);
        }
    }, [error, navigate]);

    return (
        <Tools />
    );
};

export default OAuthCallback;
