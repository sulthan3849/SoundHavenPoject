import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content = file_path.read_text(encoding='utf-8')

old_button_2 = """                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              if (!queue.some(t => t.id === track.id.toString())) {
                                addDownload({
                                  id: track.id.toString(),
                                  type: 'track',
                                  title: track.title,
                                  artist: track.artist
                                });
                              }
                            }}
                            className={`p-2 rounded-full transition-all hidden md:block ${
                              queue.some(t => t.id === track.id.toString())
                                ? "text-green-500" 
                                : "opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10"
                            }`}
                            title="Download FLAC"
                          >
                             <Download className={`w-4 h-4 ${queue.some(t => t.id === track.id.toString()) ? 'animate-pulse' : ''}`} />
                          </button>"""

new_button_2 = """                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              const queuedTask = queue.find(t => t.id === track.id.toString());
                              if (queuedTask) {
                                if (queuedTask.status === 'downloading' || queuedTask.status === 'pending') {
                                  cancelDownload(queuedTask.id);
                                  return;
                                }
                                if (queuedTask.status === 'completed') {
                                  return;
                                }
                              }
                              addDownload({
                                id: track.id.toString(),
                                type: 'track',
                                title: track.title,
                                artist: track.artist || 'Unknown',
                                cover_url: track.cover_url || (details && 'cover_url' in details ? details.cover_url : undefined)
                              });
                            }}
                            className={`p-2 rounded-full transition-all hidden md:block ${
                              queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending'
                                ? "text-red-500 hover:text-red-500 hover:bg-red-500/10" 
                                : queue.find(t => t.id === track.id.toString())?.status === 'completed'
                                ? "text-green-500/50"
                                : "opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10"
                            }`}
                            title={queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? "Cancel Download" : "Download FLAC"}
                          >
                            {queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? (
                              <X className="h-4 w-4" />
                            ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                              <Check className="h-4 w-4" />
                            ) : (
                              <Download className="h-4 w-4" />
                            )}
                          </button>"""

if old_button_2 in content:
    content = content.replace(old_button_2, new_button_2)
    print("Replaced button 2")
else:
    print("Failed to replace button 2")

file_path.write_text(content, encoding='utf-8')
