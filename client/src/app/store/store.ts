
import { configureStore } from '@reduxjs/toolkit';

import videoReducer from './videoSlice';
import chatReducer from './chatSlice';
import toolsReducer from './toolsSlice';
import summaryReducer from './summarySlice';


export const store = configureStore({
  reducer: {
    video: videoReducer,
    chat: chatReducer,
    tools: toolsReducer,
    summary: summaryReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
