import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Search, Loader2, Download, Play, Volume2, Pause, X, Check } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import VinylAlbumCard from "@/components/ui/great-ui-vinyl-album-card";
import MusicArtwork from "@/components/ui/music-artwork";
import { ProgressiveBlurModal } from "@/components/ui/progressive-blur-modal";
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item";
import { useDownloadStore } from "@/store/useDownloadStore";
import { usePlayerStore } from "@/store/usePlayerStore";
import BottomPlayerBar from "@/components/layout/BottomPlayerBar";

const API_BASE = "http://localhost:8000";

interface Track {
  id: number;
  title: string;
  artist: string;
  album: string;
  duration: number; // in seconds
  cover_url?: string;
  url: string;
}

interface Album {
  id: number;
  title: string;
  artist: string;
  release_date: string;
  cover_url?: string;
  url: string;
}

interface Playlist {
  id: string;
  title: string;
  creator: string;
  number_of_tracks: number;
  cover_url?: string;
  url: string;
}

interface Artist {
  id: number;
  name: string;
  picture_url?: string;
  url: string;
}

// Helper to format seconds to mm:ss
function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

const MOCK_TRACKS: Track[] = [
  { id: 1, title: "Search & Rescue", artist: "Drake", album: "Search & Rescue", duration: 272, cover_url: "https://a5.mzstatic.com/us/r1000/0/Music116/v4/f9/6d/dc/f96ddc30-396d-6dbb-86fe-399831a26446/23UMGIM39822.rgb.jpg", url: "" },
  { id: 2, title: "After Hours", artist: "The Weeknd", album: "After Hours", duration: 361, cover_url: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36", url: "" },
  { id: 3, title: "good 4 u", artist: "Olivia Rodrigo", album: "SOUR", duration: 178, cover_url: "https://upload.wikimedia.org/wikipedia/en/b/b2/Olivia_Rodrigo_-_SOUR.png", url: "" },
];

const MOCK_ALBUMS: Album[] = [
  { id: 1, title: "Search & Rescue", artist: "Drake", release_date: "2026-01-01", cover_url: "https://a5.mzstatic.com/us/r1000/0/Music116/v4/f9/6d/dc/f96ddc30-396d-6dbb-86fe-399831a26446/23UMGIM39822.rgb.jpg", url: "" },
  { id: 2, title: "After Hours", artist: "The Weeknd", release_date: "2020-01-01", cover_url: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36", url: "" },
  { id: 3, title: "SOUR", artist: "Olivia Rodrigo", release_date: "2021-01-01", cover_url: "https://upload.wikimedia.org/wikipedia/en/b/b2/Olivia_Rodrigo_-_SOUR.png", url: "" },
];

const MOCK_PLAYLISTS: Playlist[] = [
  { id: "1", title: "Search & Rescue", creator: "Drake", number_of_tracks: 10, cover_url: "https://a5.mzstatic.com/us/r1000/0/Music116/v4/f9/6d/dc/f96ddc30-396d-6dbb-86fe-399831a26446/23UMGIM39822.rgb.jpg", url: "" },
  { id: "2", title: "Blinding Lights", creator: "The Weeknd", number_of_tracks: 20, cover_url: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36", url: "" },
];

const MOCK_ARTISTS: Artist[] = [
  { id: 1, name: "Drake", picture_url: "", url: "" },
  { id: 2, name: "The Weeknd", picture_url: "", url: "" },
  { id: 3, name: "Olivia Rodrigo", picture_url: "", url: "" },
];

export function GlassmorphismListenAppBlock() {
  const [query, setQuery] = useState("");
  const [tracks, setTracks] = useState<Track[]>([]);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [artists, setArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  
  const [showDownloads, setShowDownloads] = useState(false);
  
  // Detail Modal State
  const [selectedDetail, setSelectedDetail] = useState<{
    isOpen: boolean;
    type: 'album' | 'playlist' | 'artist' | null;
    id: string | null;
    details: any;
    tracks: any[];
    albums?: any[];
    eps_singles?: any[];
    isLoading: boolean;
    history: any[];
  }>({
    isOpen: false,
    type: null,
    id: null,
    details: null,
    tracks: [],
    albums: [],
    eps_singles: [],
    isLoading: false,
    history: []
  });

  const handleOpenDetail = async (type: 'album' | 'playlist' | 'artist', item: any) => {
    setSelectedDetail(prev => {
      const newHistory = prev.isOpen ? [...prev.history, { ...prev, history: [] }] : [];
      return {
        isOpen: true,
        type,
        id: item.id.toString(),
        details: {
          id: item.id.toString(),
          title: item.title || item.name,
          creator: item.artist || item.creator || 'Artist',
          coverUrl: item.cover_url || item.picture_url,
          info: type === 'artist' ? 'Artist' : (item.release_date ? item.release_date.split('-')[0] : `${item.number_of_tracks || '?'} tracks`)
        },
        tracks: [],
        albums: [],
        eps_singles: [],
        isLoading: true,
        history: newHistory
      };
    });

    try {
      let endpoint = '';
      if (type === 'artist') {
         endpoint = `${API_BASE}/api/artist/${item.id}`;
      } else {
         endpoint = type === 'album' 
           ? `${API_BASE}/api/album/${item.id}/tracks`
           : `${API_BASE}/api/playlist/${item.id}/tracks`;
      }
        
      const res = await fetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        if (type === 'artist') {
          setSelectedDetail(prev => ({ 
            ...prev, 
            details: { ...prev.details, coverUrl: data.artist.picture_url || prev.details.coverUrl, info: `${data.artist.popularity || 0} fans` },
            tracks: data.top_tracks, 
            albums: data.albums,
            eps_singles: data.eps_singles,
            isLoading: false 
          }));
        } else {
          setSelectedDetail(prev => ({ ...prev, tracks: data.tracks, isLoading: false }));
        }
      } else {
        setSelectedDetail(prev => ({ ...prev, isLoading: false }));
      }
    } catch (e) {
      console.error(e);
      setSelectedDetail(prev => ({ ...prev, isLoading: false }));
    }
  };

  const { addDownload, queue, setStatus, cancelDownload, updateProgress, setTaskMetadata } = useDownloadStore();

  useEffect(() => {
    const processQueue = async () => {
      // Find first pending task
      const pendingTask = queue.find(t => t.status === 'pending');
      if (!pendingTask) return;

      // Ensure no task is currently downloading (max 1 concurrent)
      if (queue.some(t => t.status === 'downloading')) return;

      try {
        setStatus(pendingTask.id, 'downloading');
        
        if (pendingTask.type === 'track') {
          const abortController = new AbortController();
          setTaskMetadata(pendingTask.id, { abortController });
          
          const response = await fetch(`${API_BASE}/api/download/${pendingTask.id}`, {
            signal: abortController.signal
          });
          
          if (!response.ok) throw new Error(`Failed to download: ${response.statusText}`);
          
          const contentLength = response.headers.get('content-length');
          const total = contentLength ? parseInt(contentLength, 10) : 0;
          let loaded = 0;
          const chunks = [];
          
          if (response.body) {
            const reader = response.body.getReader();
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              if (value) {
                chunks.push(value);
                loaded += value.length;
                if (total) {
                  updateProgress(pendingTask.id, Math.round((loaded/total)*100));
                } else {
                  updateProgress(pendingTask.id, Math.min(99, Math.round((loaded / (1024 * 1024 * 30)) * 100)));
                }
              }
            }
          }
          
          const blob = chunks.length > 0 ? new Blob(chunks) : await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${pendingTask.artist} - ${pendingTask.title}.flac`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          setStatus(pendingTask.id, 'completed');
        } else {
          // Collection Download (Album/Playlist)
          const response = await fetch(`${API_BASE}/api/download/collection/start/${pendingTask.type}/${pendingTask.id}`);
          if (!response.ok) throw new Error("Failed to start collection download");
          
          const { task_id } = await response.json();
          setTaskMetadata(pendingTask.id, { taskId: task_id });
          
          // Poll status
          while (true) {
            // Check if user cancelled it in the meantime
            const currentTask = useDownloadStore.getState().queue.find(t => t.id === pendingTask.id);
            if (!currentTask || currentTask.status === 'cancelled') break;
            
            const statusRes = await fetch(`${API_BASE}/api/download/collection/status/${task_id}`);
            if (!statusRes.ok) throw new Error("Status check failed");
            
            const statusData = await statusRes.json();
            
            if (statusData.status === "error") {
              throw new Error(statusData.message || "Unknown error occurred");
            }
            
            if (statusData.status === "processing") {
              updateProgress(pendingTask.id, currentTask.progress > 90 ? 90 : (currentTask.progress || 0) + 1, statusData.message);
            }
            
            if (statusData.status === "ready") {
              updateProgress(pendingTask.id, 100, "Ready!");
              const a = document.createElement("a");
              a.href = `${API_BASE}/api/download/collection/file/${task_id}`;
              a.download = statusData.filename;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              setStatus(pendingTask.id, 'completed');
              break;
            }
            
            await new Promise(resolve => setTimeout(resolve, 2000));
          }
        }
      } catch (err: any) {
        if (err.name === 'AbortError') {
           // Ignored, handled by cancelDownload
        } else {
           setStatus(pendingTask.id, 'error', err.message);
        }
      }
    };

    processQueue();
  }, [queue, setStatus, setTaskMetadata, updateProgress]);
  const { playTrack, currentTrack, isPlaying, pause, resume } = usePlayerStore();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=300`);
      if (!res.ok) {
        if (res.status === 401) {
          throw new Error("TIDAL is not connected. Please log in via the Admin Dashboard.");
        }
        throw new Error("Search failed.");
      }
      const data = await res.json();
      setTracks(data.tracks || []);
      setAlbums(data.albums || []);
      setPlaylists(data.playlists || []);
      setArtists(data.artists || []);
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTrack = (track: Track, e: React.MouseEvent) => {
    e.stopPropagation(); // Mencegah terklik play
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
      artist: track.artist,
      cover_url: track.cover_url
    });
  };

  const handlePlayTrack = (track: Track, customQueue?: Track[]) => {
    if (currentTrack?.id.toString() === track.id.toString()) {
      if (isPlaying) pause();
      else resume();
    } else {
      const q = customQueue || tracks;
      playTrack({
        id: track.id.toString(),
        title: track.title,
        artist: track.artist,
        cover_url: track.cover_url
      }, q.map(t => ({
        id: t.id.toString(),
        title: t.title,
        artist: t.artist,
        cover_url: t.cover_url
      })));
    }
  };

  return (
    <section className="relative overflow-hidden px-6 py-12 md:py-32 min-h-screen">
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-0 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-foreground/[0.03] blur-3xl" />
        <div className="absolute bottom-0 right-0 h-[420px] w-[420px] rounded-full bg-foreground/[0.02] blur-3xl" />
      </div>

      <div className="mx-auto max-w-6xl pb-24">
        <Card className="relative overflow-hidden border border-border/50 bg-background/40 p-10 shadow-[0_40px_120px_rgba(15,23,42,0.25)] backdrop-blur-2xl md:p-16">
          <div className="absolute inset-0 bg-gradient-to-br from-foreground/[0.05] via-transparent to-transparent" />

          <div className="relative z-10 grid gap-12 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="space-y-10">
              <div className="space-y-5">
                <Badge
                  variant="outline"
                  className="w-fit border-border/60 bg-background/40 text-xs uppercase tracking-[0.2em] text-foreground/70 backdrop-blur"
                >
                  TIDAL DOWNLODER
                </Badge>
                <div className="space-y-4">
                  <h2 className="text-4xl font-semibold tracking-tight text-foreground md:text-5xl lg:text-6xl">
                    Sound that feels like a private concert
                  </h2>
                  <p className="max-w-xl text-base leading-relaxed text-foreground/70 md:text-lg">
                    Stream, discover, and download true FLAC music with glassy interfaces,
                    subtle motion, and immersive visuals that keep the focus on
                    the sound.
                  </p>
                </div>
              </div>

              {/* Search Form */}
              <form onSubmit={handleSearch} className="flex gap-2">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-foreground/50">
                    <Search className="h-5 w-5" />
                  </div>
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for songs, artists, or albums..."
                    className="w-full h-12 pl-12 pr-4 bg-background/60 border border-border/40 rounded-full text-foreground placeholder:text-foreground/50 focus:outline-none focus:border-border/80 backdrop-blur-xl transition-colors"
                  />
                </div>
                <Button 
                  type="submit" 
                  size="lg" 
                  className="h-12 rounded-full px-8"
                  disabled={loading || !query.trim()}
                >
                  {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Search"}
                </Button>
                
                {/* Download Queue Toggle */}
                <Button 
                  type="button" 
                  size="lg" 
                  variant="outline"
                  title="Open Download Queue"
                  className="h-12 w-12 rounded-full p-0 relative border-border/40 bg-background/40 backdrop-blur group"
                  onClick={() => setShowDownloads(!showDownloads)}
                >
                  <Download className="h-5 w-5 text-foreground/80 group-hover:text-foreground" />
                  {queue.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-green-500 text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center animate-in zoom-in">
                      {queue.length}
                    </span>
                  )}
                </Button>
              </form>

              {/* Search Tabs */}
              <div className="flex gap-2 mt-2 overflow-x-auto pb-2 scrollbar-none">
                {[
                  { id: "all", label: "All" },
                  { id: "tracks", label: "Tracks" },
                  { id: "albums", label: "Albums" },
                  { id: "playlists", label: "Playlists" },
                  { id: "profiles", label: "Profiles" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-5 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap border border-border/20 backdrop-blur-md ${
                      activeTab === tab.id
                        ? "bg-foreground text-background"
                        : "bg-background/40 text-foreground/80 hover:bg-background/80"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              
              {error && (
                <div className="text-red-400 text-sm font-medium p-4 bg-red-950/20 border border-red-900/50 rounded-xl">
                  {error}
                </div>
              )}
            </div>

            {/* Right Column Hero: Decorative Vinyl (Always visible as dashboard hero) */}
            <div className="hidden lg:flex justify-center mt-8">
              <div className="scale-[0.85] xl:scale-95 origin-top">
                <VinylAlbumCard
                  title="SOUR"
                  artist="Olivia Rodrigo"
                  year="2021"
                  releaseType="FLAC Ã¢â‚¬Â¢ 16-bit 44.1kHz"
                  coverImage="https://upload.wikimedia.org/wikipedia/en/b/b2/Olivia_Rodrigo_-_SOUR.png"
                />
              </div>
            </div>
          </div>

          <div className="relative z-10 mt-12">
            {/* Conditional Content Area */}
            <div className="w-full">
                {activeTab === "all" && (
                  <div className="w-full">
                    {tracks.length === 0 && artists.length === 0 && !loading ? (
                      <div className="text-foreground/50 py-12 text-center border border-dashed border-border/40 rounded-3xl bg-background/20 backdrop-blur-sm max-w-2xl">
                         Ketikkan sesuatu di atas untuk mencari lagu, album, atau playlist di TIDAL.
                      </div>
                    ) : (
                      <div className="space-y-10">
                        {/* Top Artist & Tracks Row */}
                        <div className="flex flex-col xl:flex-row gap-8">
                          {artists.length > 0 && (
                            <div className="w-full xl:w-1/3 flex flex-col gap-4">
                              <h3 className="text-xl font-semibold tracking-tight text-foreground">Top result</h3>
                              <div 
                                className="flex flex-col gap-4 p-6 rounded-2xl bg-background/10 border border-border/10 backdrop-blur-md hover:bg-background/20 transition-colors cursor-pointer group h-full"
                                onClick={() => handleOpenDetail('artist', artists[0])}
                              >
                                <Avatar className="w-24 h-24 shadow-xl border-0">
                                  <AvatarImage src={artists[0].picture_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(artists[0].name)}&background=random`} className="object-cover" />
                                  <AvatarFallback className="text-xl font-bold bg-background/40">{artists[0].name.charAt(0)}</AvatarFallback>
                                </Avatar>
                                <div className="mt-auto">
                                  <h4 className="font-bold text-foreground text-3xl group-hover:underline">{artists[0].name}</h4>
                                  <Badge variant="outline" className="text-[10px] bg-background/20 mt-2 text-foreground/60 border-0 px-0">Artist</Badge>
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {tracks.length > 0 && (
                            <div className="w-full xl:flex-1 flex flex-col gap-4">
                              <h3 className="text-xl font-semibold tracking-tight text-foreground">Tracks</h3>
                              <div className="flex flex-col gap-1">
                                {tracks.slice(0, 5).map((track, i) => {
                                  const isActive = currentTrack?.id === track.id.toString();
                                  return (
                                    <div key={track.id} className={`flex items-center gap-4 p-2 rounded-xl transition-colors cursor-pointer group ${isActive ? 'bg-background/30' : 'hover:bg-background/20'}`} onClick={() => {
                                      if (isActive) isPlaying ? pause() : resume();
                                      else handlePlayTrack(track);
                                    }}>
                                      <div className="relative w-12 h-12 rounded-md overflow-hidden bg-neutral-800 shrink-0">
                                        {track.cover_url && <img src={track.cover_url} alt={track.title} className="w-full h-full object-cover" />}
                                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                          {isActive && isPlaying ? <Pause className="w-5 h-5 text-white fill-white" /> : <Play className="w-5 h-5 text-white fill-white" />}
                                        </div>
                                      </div>
                                      <div className="flex-1 overflow-hidden">
                                        <h4 className={`font-semibold text-[14px] truncate ${isActive ? 'text-yellow-500' : 'text-foreground group-hover:underline'}`}>{track.title}</h4>
                                        <p className="text-[13px] text-foreground/60 truncate hover:underline hover:text-foreground">{track.artist}</p>
                                      </div>
                              <button
                                onClick={(e) => handleDownloadTrack(track, e)}
                                className={`p-2 rounded-full transition-all ${
                                  queue.some(t => t.id === track.id.toString() && (t.status === 'pending' || t.status === 'downloading'))
                                    ? "text-red-500 hover:bg-red-500/10" 
                                    : queue.some(t => t.id === track.id.toString() && t.status === 'completed')
                                    ? "text-green-500"
                                    : "text-foreground/40 hover:text-foreground hover:bg-foreground/10"
                                }`}
                                title="Download FLAC"
                              >
                                {queue.find(t => t.id === track.id.toString()) && (queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending') ? (
                                  <X className="h-4 w-4" />
                                ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                                  <Check className="h-4 w-4" />
                                ) : (
                                  <Download className="h-4 w-4" />
                                )}
                              </button>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Albums Row */}
                        {albums.length > 0 && (
                          <div className="flex flex-col gap-4">
                            <h3 className="text-xl font-semibold tracking-tight text-foreground">Albums</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-16 gap-y-16 pl-2 pr-16 pb-12">
                              {albums.slice(0, 3).map(album => (
                                <div key={album.id} className="w-full cursor-pointer" onClick={() => handleOpenDetail('album', album)}>
                                  <VinylAlbumCard 
                                    title={album.title} 
                                    artist={album.artist} 
                                    year={album.release_date ? album.release_date.split('-')[0] : "Unknown"} 
                                    releaseType="Album" 
                                    coverImage={album.cover_url || "https://upload.wikimedia.org/wikipedia/commons/c/c9/Vinyl_record.svg"}
                                  />
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Playlists Row */}
                        {playlists.length > 0 && (
                          <div className="flex flex-col gap-4">
                            <h3 className="text-xl font-semibold tracking-tight text-foreground">Playlists</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-16 gap-y-16 pl-12 pr-12 pb-12">
                              {playlists.slice(0, 3).map(playlist => (
                                <div key={playlist.id} className="w-full cursor-pointer" onClick={() => handleOpenDetail('playlist', playlist)}>
                                  <MusicArtwork
                                    artist={playlist.creator}
                                    music={playlist.title}
                                    albumArt={playlist.cover_url || "https://upload.wikimedia.org/wikipedia/commons/c/c9/Vinyl_record.svg"}
                                    isSong={false}
                                  />
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "albums" && (
                  <div className="pt-4 space-y-4">
                    <h3 className="text-xl font-semibold tracking-tight text-foreground mb-8">Albums</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-16 gap-y-16 pl-2 pr-16 pb-12">
                      {albums.map(album => (
                        <div key={album.id} className="w-full cursor-pointer" onClick={() => handleOpenDetail('album', album)}>
                          <VinylAlbumCard 
                            title={album.title} 
                            artist={album.artist} 
                            year={album.release_date ? album.release_date.split('-')[0] : "Unknown"} 
                            releaseType="Album" 
                            coverImage={album.cover_url || "https://upload.wikimedia.org/wikipedia/commons/c/c9/Vinyl_record.svg"}
                          />
                        </div>
                      ))}
                      {albums.length === 0 && !loading && (
                        <div className="text-foreground/50 col-span-2 text-sm">No albums found. Try searching first.</div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === "playlists" && (
                  <div className="pt-4 space-y-4">
                    <h3 className="text-xl font-semibold tracking-tight text-foreground mb-8">Playlists</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-16 gap-y-16 pl-12 pr-12 pb-12">
                      {playlists.map(playlist => (
                        <div key={playlist.id} className="w-full cursor-pointer" onClick={() => handleOpenDetail('playlist', playlist)}>
                          <MusicArtwork
                            artist={playlist.creator}
                            music={playlist.title}
                            albumArt={playlist.cover_url || "https://upload.wikimedia.org/wikipedia/commons/c/c9/Vinyl_record.svg"}
                            isSong={false}
                          />
                        </div>
                      ))}
                      {playlists.length === 0 && !loading && (
                        <div className="text-foreground/50 col-span-2 text-sm">No playlists found. Try searching first.</div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === "tracks" && (
                  <div className="pt-4 space-y-4 w-full">
                    <h3 className="text-xl font-semibold tracking-tight text-foreground">Top Tracks</h3>
                    <div className="w-full">
                      <div className="hidden md:grid grid-cols-[auto_1fr_1fr_auto] gap-4 px-4 pb-2 text-xs font-medium text-foreground/50 border-b border-border/20 mb-4">
                        <div className="w-8 text-center">#</div>
                        <div>TITLE</div>
                        <div>ALBUM</div>
                        <div className="w-24 text-right">TIME</div>
                      </div>
                      <div className="space-y-2">
                        {tracks.map((track, i) => {
                          const isActive = currentTrack?.id === track.id.toString();
                          return (
                          <div key={track.id} className={`flex items-center gap-4 p-3 rounded-2xl border border-border/20 backdrop-blur-md transition-colors cursor-pointer group ${isActive ? 'bg-background/30' : 'bg-background/20 hover:bg-background/40'}`} onClick={() => {
                            if (isActive) isPlaying ? pause() : resume();
                            else handlePlayTrack(track);
                          }}>
                            <div className={`w-8 text-center text-sm font-medium ${isActive ? 'text-yellow-500' : 'text-foreground/50 group-hover:text-foreground'}`}>
                              {isActive ? (
                                isPlaying ? (
                                  <>
                                    <Volume2 className="w-4 h-4 mx-auto animate-pulse text-yellow-500 block group-hover:hidden" />
                                    <Pause className="w-4 h-4 mx-auto fill-current text-yellow-500 hidden group-hover:block" />
                                  </>
                                ) : (
                                  <Play className="w-4 h-4 mx-auto fill-current text-yellow-500" />
                                )
                              ) : (
                                <>
                                  <span className="block group-hover:hidden">{i + 1}</span>
                                  <Play className="w-4 h-4 hidden group-hover:block mx-auto fill-current" />
                                </>
                              )}
                            </div>
                            <div className="relative w-12 h-12 rounded-xl overflow-hidden bg-neutral-800 shadow-md shrink-0">
                              {track.cover_url ? (
                                 <img src={track.cover_url} alt={track.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                              ) : null}
                              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                 {isActive && isPlaying ? <Pause className="w-5 h-5 text-white fill-white" /> : <Play className="w-5 h-5 text-white fill-white" />}
                              </div>
                            </div>
                            <div className="flex-1 overflow-hidden min-w-0">
                              <h4 className={`font-semibold truncate text-sm ${isActive ? 'text-yellow-500' : 'text-foreground'}`}>{track.title}</h4>
                              <p className="text-xs text-foreground/60 truncate">{track.artist}</p>
                            </div>
                            <div className="flex-1 overflow-hidden min-w-0 hidden md:block">
                              <p className="text-sm text-foreground/60 truncate">{track.album}</p>
                            </div>
                            <div className="flex items-center gap-4 w-24 shrink-0 justify-end">
                              <button
                                onClick={(e) => handleDownloadTrack(track, e)}
                                className={`p-2 rounded-full transition-all ${
                                  queue.some(t => t.id === track.id.toString() && (t.status === 'pending' || t.status === 'downloading'))
                                    ? "text-red-500 hover:bg-red-500/10" 
                                    : queue.some(t => t.id === track.id.toString() && t.status === 'completed')
                                    ? "text-green-500"
                                    : "text-foreground/40 hover:text-foreground hover:bg-foreground/10"
                                }`}
                                title="Download FLAC"
                              >
                                {queue.find(t => t.id === track.id.toString()) && (queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending') ? (
                                  <X className="h-4 w-4" />
                                ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                                  <Check className="h-4 w-4" />
                                ) : (
                                  <Download className="h-4 w-4" />
                                )}
                              </button>
                              <div className={`text-sm font-medium tabular-nums ${isActive ? 'text-yellow-500/80' : 'text-foreground/50'}`}>
                                {formatTime(track.duration)}
                              </div>
                            </div>
                          </div>
                          );
                        })}
                      </div>
                      {tracks.length === 0 && !loading && (
                         <div className="text-foreground/50 text-sm py-4">No tracks found. Try searching first.</div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === "profiles" && (
                  <div className="pt-4">
                    <h3 className="text-xl font-semibold tracking-tight text-foreground mb-6">Profiles</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
                      {artists.length > 0 ? artists.map((artist, idx) => (
                        <div key={idx} className="flex flex-col items-center gap-3 cursor-pointer group" onClick={() => handleOpenDetail('artist', artist)}>
                          <Avatar className="w-full aspect-square h-auto border-0 shadow-lg">
                            <AvatarImage src={artist.picture_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(artist.name)}&background=random`} className="object-cover" />
                            <AvatarFallback className="text-3xl font-bold bg-background/40">{artist.name.charAt(0)}</AvatarFallback>
                          </Avatar>
                          <div className="text-center w-full mt-1">
                            <span className="font-bold text-[14px] text-foreground truncate block">{artist.name}</span>
                            <span className="text-[11px] font-bold text-foreground/40 uppercase mt-0.5 block">Artist</span>
                          </div>
                        </div>
                      )) : (
                        Array.from(new Set(tracks.map(t => t.artist))).map((artistName, idx) => (
                          <div key={idx} className="flex flex-col items-center gap-3 cursor-pointer group" onClick={() => handleOpenDetail('artist', { name: artistName, id: artistName } as any)}>
                            <Avatar className="w-full aspect-square h-auto border-0 shadow-lg">
                              <AvatarImage src={`https://ui-avatars.com/api/?name=${encodeURIComponent(artistName)}&background=random`} className="object-cover" />
                              <AvatarFallback className="text-3xl font-bold bg-background/40">{artistName.charAt(0)}</AvatarFallback>
                            </Avatar>
                            <div className="text-center w-full mt-1">
                              <span className="font-bold text-[14px] text-foreground truncate block">{artistName}</span>
                              <span className="text-[11px] font-bold text-foreground/40 uppercase mt-0.5 block">Artist</span>
                            </div>
                          </div>
                        ))
                      )}
                      {artists.length === 0 && tracks.length === 0 && !loading && (
                         <div className="text-foreground/50 col-span-2 text-sm">No profiles found. Try searching first.</div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab !== "all" && activeTab !== "albums" && activeTab !== "playlists" && activeTab !== "tracks" && activeTab !== "profiles" && (
                   <div className="text-foreground/50 py-12 text-center border border-dashed border-border/40 rounded-3xl bg-background/20 backdrop-blur-sm">
                     Kategori <b>{activeTab}</b> sedang dalam pengembangan.
                   </div>
                )}
              </div>
            </div>

          </Card>
      </div>

      {/* Embedded Bottom Player Bar (Appears when a track is clicked) */}
      {currentTrack && (
        <div className="fixed bottom-0 left-0 w-full z-[200] animate-in slide-in-from-bottom-2 duration-300">
          <BottomPlayerBar />
        </div>
      )}

      {/* Slide-out Download Manager Panel */}
      <div 
        className={`fixed top-0 right-0 h-full w-full max-w-sm bg-background/80 backdrop-blur-3xl border-l border-border/50 shadow-2xl z-50 transition-transform duration-500 ease-out flex flex-col ${
          showDownloads ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="p-6 border-b border-border/30 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold">Download Queue</h3>
            <p className="text-sm text-foreground/50">{queue.length} items in queue</p>
          </div>
          <Button variant="ghost" size="icon" className="rounded-full" onClick={() => setShowDownloads(false)}>
            <X className="w-5 h-5" />
          </Button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {queue.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 text-foreground/40">
              <Download className="w-12 h-12 opacity-20" />
              <p>Your queue is empty.<br/>Start downloading some true lossless music.</p>
            </div>
          ) : (
            queue.map((task, idx) => (
              <div key={`${task.id}-${idx}`} className="bg-background/40 border border-border/40 rounded-xl p-4 flex flex-col gap-3 relative overflow-hidden">
                <div className="flex items-center gap-3 z-10">
                  {task.cover_url && (
                    <img src={task.cover_url} alt="Cover" className="w-10 h-10 rounded shadow-sm object-cover" />
                  )}
                  <div className="overflow-hidden flex-1">
                    <h5 className="font-semibold text-sm truncate">{task.title}</h5>
                    <p className="text-xs text-foreground/60 truncate">{task.artist}</p>
                  </div>
                  <Badge variant="outline" className={`text-[10px] capitalize whitespace-nowrap ${
                    task.status === 'completed' ? 'text-green-500 border-green-500/30' :
                    task.status === 'downloading' ? 'text-blue-400 border-blue-400/30' :
                    task.status === 'cancelled' ? 'text-orange-400 border-orange-400/30' :
                    task.status === 'error' ? 'text-red-400 border-red-400/30' :
                    'text-foreground/50'
                  }`}>
                    {task.status}
                  </Badge>
                </div>
                
                {(task.status === 'pending' || task.status === 'downloading') && (
                  <div className="flex flex-col gap-2 z-10">
                    {task.message && (
                      <p className="text-[10px] text-blue-400/80 italic">{task.message}</p>
                    )}
                    <div className="flex items-center gap-3">
                      <div className="h-1.5 flex-1 bg-background/60 rounded-full overflow-hidden relative">
                        <div 
                          className={`h-full rounded-full transition-all duration-300 ${task.status === 'pending' ? 'w-[5%] bg-foreground/20' : 'bg-blue-500'}`}
                          style={{ width: task.status === 'downloading' ? `${task.progress || 5}%` : undefined }}
                        />
                      </div>
                      {task.status === 'downloading' && task.progress > 0 && (
                        <span className="text-[10px] font-medium text-blue-400 w-6 text-right tabular-nums">
                          {task.progress}%
                        </span>
                      )}
                      <button 
                        onClick={() => cancelDownload(task.id)}
                        className="p-1 rounded-full text-foreground/40 hover:text-red-400 hover:bg-red-400/10 transition-colors"
                        title="Cancel Download"
                      >
                        <span className="text-sm font-bold leading-none block w-4 h-4 text-center">×</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Subtle background gradient based on status */}
                {task.status === 'completed' && <div className="absolute inset-0 bg-green-500/5 z-0" />}
                {task.status === 'downloading' && <div className="absolute inset-0 bg-blue-500/5 z-0" />}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Detail View Modal */}
      <ProgressiveBlurModal
        isOpen={selectedDetail.isOpen}
        onClose={() => setSelectedDetail(prev => {
          if (prev.history && prev.history.length > 0) {
            const previousState = prev.history[prev.history.length - 1];
            return { ...previousState, history: prev.history.slice(0, -1) };
          }
          return { ...prev, isOpen: false, history: [] };
        })}
        type={selectedDetail.type}
        details={selectedDetail.details}
        tracks={selectedDetail.tracks}
        albums={selectedDetail.albums}
        eps_singles={selectedDetail.eps_singles}
        isLoading={selectedDetail.isLoading}
        onOpenDetail={handleOpenDetail}
        onPlayTrack={handlePlayTrack}
        currentTrackId={currentTrack?.id}
        isPlaying={isPlaying}
      />
    </section>
  );
}


