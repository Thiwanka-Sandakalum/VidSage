import React from 'react';
import { AspectRatio, Image, Badge, Box } from '@mantine/core';

interface VideoThumbnailProps {
    thumbnail: string;
    title: string;
    duration?: string;
    width?: number | string;
    showPlayOverlay?: boolean;
    videoId?: string;
}

const VideoThumbnail: React.FC<VideoThumbnailProps> = ({
    thumbnail,
    title,
    duration,
    width,
    showPlayOverlay = true,
    videoId
}) => {
    // Get high-quality YouTube thumbnail
    const youtubeThumb = videoId
        ? `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`
        : thumbnail;

    return (
        <AspectRatio
            ratio={16 / 9}
            style={{
                width,
                position: 'relative',
                borderRadius: 8,
                overflow: 'hidden'
            }}
        >
            <Image src={youtubeThumb} alt={title} fallbackSrc={thumbnail} />
            {showPlayOverlay && (
                <Box
                    className="play-overlay"
                    style={{
                        position: 'absolute',
                        inset: 0,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        opacity: 0,
                        transition: 'opacity 0.2s ease'
                    }}
                >
                    <i className="fas fa-play" style={{ color: 'white', fontSize: '2rem' }}></i>
                </Box>
            )}
        </AspectRatio>
    );
};

export default VideoThumbnail;
