import { create } from 'zustand';

export interface DownloadTask {
  id: string; // TIDAL ID
  type: 'track' | 'album' | 'playlist';
  title: string;
  artist: string;
  progress: number; // 0-100
  status: 'pending' | 'downloading' | 'completed' | 'error' | 'cancelled';
  error?: string;
  message?: string; // For collection dynamic status
  taskId?: string; // Backend task ID for collections
  cover_url?: string;
  abortController?: AbortController; // To cancel fetch stream for tracks
}

interface DownloadState {
  queue: DownloadTask[];
  addDownload: (task: Omit<DownloadTask, 'progress' | 'status'>) => void;
  updateProgress: (id: string, progress: number, message?: string) => void;
  setStatus: (id: string, status: DownloadTask['status'], error?: string) => void;
  setTaskMetadata: (id: string, metadata: { taskId?: string; abortController?: AbortController }) => void;
  removeDownload: (id: string) => void;
  cancelDownload: (id: string) => Promise<void>;
}

export const useDownloadStore = create<DownloadState>((set, get) => ({
  queue: [],
  addDownload: (task) => set((state) => {
    // Prevent duplicate active downloads
    if (state.queue.some(t => t.id === task.id && ['pending', 'downloading'].includes(t.status))) {
      return state;
    }
    
    // If the task already exists (e.g., cancelled or completed), remove the old one so it can be re-added
    const filteredQueue = state.queue.filter(t => t.id !== task.id);
    
    return {
      queue: [...filteredQueue, { ...task, progress: 0, status: 'pending' }]
    };
  }),
  updateProgress: (id, progress, message) => set((state) => ({
    queue: state.queue.map(task => 
      task.id === id ? { ...task, progress, ...(message ? { message } : {}) } : task
    )
  })),
  setStatus: (id, status, error) => set((state) => ({
    queue: state.queue.map(task => 
      task.id === id ? { ...task, status, error } : task
    )
  })),
  setTaskMetadata: (id, metadata) => set((state) => ({
    queue: state.queue.map(task => 
      task.id === id ? { ...task, ...metadata } : task
    )
  })),
  removeDownload: (id) => set((state) => ({
    queue: state.queue.filter(task => task.id !== id)
  })),
  cancelDownload: async (id) => {
    const task = get().queue.find(t => t.id === id);
    if (!task) return;
    
    // Abort track stream if present
    if (task.abortController) {
      task.abortController.abort();
    }
    
    // Cancel backend collection task if present
    if (task.taskId && (task.type === 'album' || task.type === 'playlist')) {
      try {
        await fetch(`http://localhost:8000/api/download/collection/cancel/${task.taskId}`, {
          method: 'DELETE'
        });
      } catch (e) {
        console.error("Failed to cancel collection download:", e);
      }
    }
    
    set((state) => ({
      queue: state.queue.map(t => 
        t.id === id ? { ...t, status: 'cancelled', message: 'Cancelled' } : t
      )
    }));
  }
}));

