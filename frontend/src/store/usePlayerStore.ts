import { create } from 'zustand';

export interface PlayableTrack {
  id: string | number;
  title: string;
  artist: string;
  cover_url?: string;
  preview_url?: string;
}

interface PlayerState {
  currentTrack: PlayableTrack | null;
  isPlaying: boolean;
  queue: PlayableTrack[];
  playTrack: (track: PlayableTrack, queue?: PlayableTrack[]) => Promise<void>;
  pause: () => void;
  resume: () => void;
  stop: () => void;
  playNext: () => void;
  playPrev: () => void;
}

export const usePlayerStore = create<PlayerState>((set, get) => ({
  currentTrack: null,
  isPlaying: false,
  queue: [],
  playTrack: async (track, queue) => {
    set({ 
      currentTrack: {
        ...track,
        preview_url: track.preview_url || "" 
      }, 
      isPlaying: true,
      ...(queue ? { queue } : {})
    });

    if (!track.preview_url) {
      try {
        const query = encodeURIComponent(`${track.title} ${track.artist}`);
        const res = await fetch(`https://itunes.apple.com/search?term=${query}&entity=song&limit=1`);
        const data = await res.json();
        
        if (data.results && data.results.length > 0 && data.results[0].previewUrl) {
          set((state) => {
            if (state.currentTrack?.id.toString() === track.id.toString()) {
              return { 
                currentTrack: { ...state.currentTrack, preview_url: data.results[0].previewUrl }
              };
            }
            return state;
          });
        }
      } catch (e) {
        console.error("Failed to fetch audio preview:", e);
      }
    }
  },
  pause: () => set({ isPlaying: false }),
  resume: () => set({ isPlaying: true }),
  stop: () => set({ currentTrack: null, isPlaying: false }),
  playNext: () => {
    const { currentTrack, queue, playTrack } = get();
    if (!currentTrack || queue.length === 0) return;
    const idx = queue.findIndex(t => t.id.toString() === currentTrack.id.toString());
    if (idx !== -1 && idx < queue.length - 1) {
      playTrack(queue[idx + 1], queue);
    }
  },
  playPrev: () => {
    const { currentTrack, queue, playTrack } = get();
    if (!currentTrack || queue.length === 0) return;
    const idx = queue.findIndex(t => t.id.toString() === currentTrack.id.toString());
    if (idx > 0) {
      playTrack(queue[idx - 1], queue);
    }
  },
}));
