import React, { useEffect, useState } from 'react';
import {
  Container,
  Stack,
  Group,
  Pagination
} from '@mantine/core';
import { fetchHistory, deleteVideo } from '../store/videoSlice';
import { useAppDispatch, useAppSelector } from '../hooks';
import HistoryEmpty from '../components/history/HistoryEmpty';
import HistoryHeader from '../components/history/HistoryHeader';
import HistoryPaginationInfo from '../components/history/HistoryPaginationInfo';
import HistorySkeleton from '../components/history/HistorySkeleton';
import VideoGrid from '../components/history/VideoGrid';
import VideoList from '../components/history/VideoList';


const History: React.FC = () => {
  const dispatch = useAppDispatch();
  const { history } = useAppSelector((state) => state.video);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(9);
  const [loading, setLoading] = useState(true);

  const totalPages = Math.ceil(history.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedVideos = history.slice(startIndex, endIndex);

  useEffect(() => {
    dispatch(fetchHistory()).finally(() => setLoading(false));
  }, [dispatch]);

  const handleDelete = async (videoId: string) => {
    await dispatch(deleteVideo(videoId));
    dispatch(fetchHistory());
  };

  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalPages, currentPage]);

  return (
    <Container size="xl" py={40}>
      <Stack gap="xl">
        <HistoryHeader
          historyLength={history.length}
          viewMode={viewMode}
          setViewMode={setViewMode}
          itemsPerPage={itemsPerPage}
          setItemsPerPage={setItemsPerPage}
          setCurrentPage={setCurrentPage}
        />

        {loading ? (
          <HistorySkeleton />
        ) : history.length > 0 ? (
          <>
            {viewMode === 'grid' ? (
              <VideoGrid videos={paginatedVideos} onDelete={handleDelete} />
            ) : (
              <VideoList videos={paginatedVideos} onDelete={handleDelete} />
            )}

            {totalPages > 1 && (
              <Group justify="center" mt="xl">
                <Pagination
                  value={currentPage}
                  onChange={setCurrentPage}
                  total={totalPages}
                  size="lg"
                  radius="md"
                  withEdges
                />
              </Group>
            )}

            <HistoryPaginationInfo
              startIndex={startIndex}
              endIndex={endIndex}
              total={history.length}
              currentPage={currentPage}
              totalPages={totalPages}
            />
          </>
        ) : (
          <HistoryEmpty />
        )}
      </Stack>
    </Container>
  );
};

export default History;
