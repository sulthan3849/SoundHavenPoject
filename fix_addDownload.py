import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/store/useDownloadStore.ts')
content = file_path.read_text(encoding='utf-8')

old_add = """  addDownload: (task) => set((state) => {
    // Prevent duplicate active downloads
    if (state.queue.some(t => t.id === task.id && ['pending', 'downloading'].includes(t.status))) {
      return state;
    }
    return {
      queue: [...state.queue, { ...task, progress: 0, status: 'pending' }]
    };
  }),"""

new_add = """  addDownload: (task) => set((state) => {
    // Prevent duplicate active downloads
    if (state.queue.some(t => t.id === task.id && ['pending', 'downloading'].includes(t.status))) {
      return state;
    }
    
    // If the task already exists (e.g., cancelled or completed), remove the old one so it can be re-added
    const filteredQueue = state.queue.filter(t => t.id !== task.id);
    
    return {
      queue: [...filteredQueue, { ...task, progress: 0, status: 'pending' }]
    };
  }),"""

if old_add in content:
    content = content.replace(old_add, new_add)
    print("Replaced addDownload")
else:
    print("Failed to replace addDownload")

file_path.write_text(content, encoding='utf-8')
