import React from 'react';
import { ActionIcon, Tooltip } from '@mantine/core';

interface DeleteButtonProps {
    onDelete: (e: React.MouseEvent) => void;
    position?: 'absolute' | 'relative';
}

const DeleteButton: React.FC<DeleteButtonProps> = ({ onDelete, position = 'relative' }) => {
    const buttonStyle = position === 'absolute'
        ? { position: 'absolute' as const, top: 8, right: 8, opacity: 0.9 }
        : {};

    return (
        <Tooltip label="Delete Video">
            <ActionIcon
                variant={position === 'absolute' ? 'filled' : 'light'}
                color="red"
                size={position === 'absolute' ? 'md' : 'lg'}
                radius="md"
                onClick={onDelete}
                style={buttonStyle}
            >
                <i className={`fas fa-trash-alt ${position === 'absolute' ? 'text-xs' : ''}`}></i>
            </ActionIcon>
        </Tooltip>
    );
};

export default DeleteButton;
