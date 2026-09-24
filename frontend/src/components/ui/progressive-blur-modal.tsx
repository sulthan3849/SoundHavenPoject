import React, { useState, useEffect } from 'react';
import { X, Play, Heart, MoreHorizontal, Download, Volume2, Pause, Check } from 'lucide-react';
import { usePlayerStore } from '@/store/usePlayerStore';
import { useDownloadStore } from '@/store/useDownloadStore';
import VinylAlbumCard from '@/components/ui/great-ui-vinyl-album-card';

export interface Track {
  id: number;
  title: string;
  artist: string;
  duration: number;
  track_number: number;
  explicit: boolean;
  cover_url: string;
}

export interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'album' | 'playlist' | 'artist' | null;
  details: {
    title: string;
    creator: string;
    coverUrl: string;
    info: string;
  } | null;
  tracks: Track[];
  albums?: any[];
  eps_singles?: any[];
  isLoading: boolean;
  onOpenDetail?: (type: 'album' | 'playlist', item: any) => void;
  onPlayTrack?: (track: Track, customQueue?: Track[]) => void;
  currentTrackId?: string;
  isPlaying?: boolean;
}

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const formatTotalDuration = (seconds: number) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
};

export const ProgressiveBlurModal = ({
  isOpen,
  onClose,
  type,
  details,
  tracks,
  albums,
  eps_singles,
  isLoading,
  onOpenDetail,
  onPlayTrack,
  currentTrackId,
  isPlaying
}: DetailModalProps) => {
  const [mounted, setMounted] = useState(false);
  const { pause, resume } = usePlayerStore();
  const { addDownload, queue, cancelDownload } = useDownloadStore();

  useEffect(() => {
    setMounted(true);
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const isThisAlbumActive = tracks.some(t => t.id.toString() === currentTrackId);

  const handleGlobalPlay = () => {
    if (tracks.length === 0) return;
    
    if (isThisAlbumActive) {
      if (isPlaying) {
        pause();
      } else {
        resume();
      }
    } else if (onPlayTrack) {
      onPlayTrack(tracks[0], tracks);
    }
  };

  const queuedCollection = details && 'id' in details && details.id ? queue.find(t => t.id === details.id.toString() && (t.type === 'album' || t.type === 'playlist')) : undefined;

  const handleDownloadAll = () => {
    if (type === 'artist') {
      tracks.forEach(track => {
        const queuedTask = queue.find(t => t.id === track.id.toString());
        if (!queuedTask || queuedTask.status === 'error' || queuedTask.status === 'cancelled') {
          addDownload({
            id: track.id.toString(),
            type: 'track',
            title: track.title,
            artist: track.artist,
            cover_url: track.cover_url || (details && 'picture_url' in details ? details.picture_url : (details && 'coverUrl' in details ? details.coverUrl : undefined))
          });
        }
      });
    } else if (details && 'id' in details) {
      if (!queuedCollection || queuedCollection.status === 'error' || queuedCollection.status === 'cancelled') {
        addDownload({
          id: details.id.toString(),
          type: type as 'album' | 'playlist',
          title: details.title,
          artist: ('artist' in details ? details.artist : ('creator' in details ? details.creator : 'Unknown')) as string,
          cover_url: ('coverUrl' in details ? details.coverUrl : ('cover_url' in details ? details.cover_url : undefined)) as string | undefined
        });
      }
    }
  };

  if (!isOpen || !mounted) return null;

  if (type === 'artist') {
    return (
      <div className="fixed inset-0 z-[100] flex animate-in fade-in duration-300">
        {/* Background layer with blurred cover image */}
        <div className="absolute inset-0 bg-neutral-950">
          {details?.coverUrl && (
            <div 
              className="absolute inset-0 opacity-40 bg-cover bg-center"
              style={{ 
                backgroundImage: `url(${details.coverUrl})`,
                filter: 'brightness(1.2) saturate(1.5) blur(80px)',
                transform: 'scale(1.1)' 
              }}
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/60 to-black/95" />
        </div>

        <div className="relative w-full h-full flex flex-col overflow-y-auto overflow-x-hidden custom-scrollbar pb-32 z-10">
          <button 
            onClick={onClose}
            className="absolute top-6 right-6 z-50 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white backdrop-blur-md transition-colors border border-white/10"
          >
            <X className="w-6 h-6" />
          </button>
          
          <div className="w-full max-w-6xl mx-auto px-6 md:px-12 pt-24 md:pt-32 pb-16 flex flex-col items-center md:items-start">
             {/* Hero Section */}
             <div className="flex flex-col md:flex-row gap-8 items-center md:items-end w-full mb-16">
               <div className="relative w-48 h-48 md:w-64 md:h-64 rounded-full overflow-hidden shadow-2xl shrink-0 border-4 border-white/10">
                 {details?.coverUrl ? (
                   <img src={details.coverUrl} className="w-full h-full object-cover" alt="" />
                 ) : (
                   <div className="w-full h-full bg-neutral-800 animate-pulse" />
                 )}
               </div>
               <div className="flex flex-col gap-4 text-center md:text-left">
                 <h1 className="text-4xl md:text-7xl font-bold text-white tracking-tight drop-shadow-sm">{details?.title}</h1>
                 <p className="text-neutral-300 text-sm md:text-base font-medium">{details?.info}</p>
                 <div className="flex gap-4 mt-2 justify-center md:justify-start">
                   <button 
                     className="h-12 px-8 bg-white hover:bg-neutral-200 text-black rounded-full font-bold flex items-center justify-center gap-2 transition-transform active:scale-95 shadow-lg"
                     onClick={handleGlobalPlay}
                   >
                     {isPlaying ? <Pause className="w-5 h-5 fill-black" /> : <Play className="w-5 h-5 fill-black" />}
                     {isPlaying ? 'Pause' : 'Play'}
                   </button>
                    <div className="flex items-center gap-2">
                      <button 
                         onClick={handleDownloadAll}
                         disabled={!!queuedCollection && queuedCollection.status !== 'error' && queuedCollection.status !== 'cancelled'}
                         className={`h-12 px-6 rounded-full font-bold flex items-center justify-center gap-2 transition-all active:scale-95 border relative overflow-hidden ${
                           queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')
                             ? "bg-blue-500/10 text-blue-400 border-blue-500/20" 
                             : queuedCollection?.status === 'completed'
                             ? "bg-green-500/10 text-green-400 border-green-500/20"
                             : "bg-white/10 hover:bg-white/20 text-white border-white/10"
                         }`}
                       >
                         {queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') && (
                           <div className="absolute inset-0 bg-blue-500/10 animate-pulse" />
                         )}
                         <Download className={`w-5 h-5 z-10 ${queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') ? 'animate-bounce' : ''}`} />
                         <span className="z-10">
                           {queuedCollection 
                             ? (queuedCollection.status === 'downloading' ? `Downloading...` : 
                                queuedCollection.status === 'pending' ? 'Queued' : 
                                queuedCollection.status === 'completed' ? 'Downloaded' : 'Download All') 
                             : 'Download All'}
                         </span>
                       </button>
                       {queuedCollection && (queuedCollection.status === 'downloading' || queuedCollection.status === 'pending') && (
                         <button
                           onClick={(e) => { e.stopPropagation(); cancelDownload(queuedCollection.id); }}
                           className="h-12 w-12 rounded-full flex items-center justify-center border border-white/10 bg-white/5 hover:bg-red-500/20 hover:text-red-500 hover:border-red-500/30 transition-all"
                           title="Cancel Download"
                         >
                           <X className="w-5 h-5" />
                         </button>
                       )}
                     </div>
                 </div>
               </div>
             </div>

             {/* Top Tracks */}
             {tracks && tracks.length > 0 && (
               <div className="w-full mb-16">
                 <h2 className="text-2xl font-bold text-white mb-6">Top Tracks</h2>
                 <div className="w-full bg-black/20 backdrop-blur-sm rounded-2xl border border-white/5 p-4 md:p-6 shadow-2xl">
                   <div className="hidden md:grid grid-cols-[auto_1fr_auto] gap-4 px-4 py-3 border-b border-neutral-700/50 text-xs font-semibold tracking-widest text-neutral-400 mb-2">
                     <div className="w-8 text-center">#</div>
                     <div>TITLE</div>
                     <div className="w-16 text-right">TIME</div>
                   </div>
                   <div className="space-y-1">
                     {tracks.map((track, i) => {
                       const isActive = currentTrackId === track.id.toString();
                       return (
                         <div 
                           key={track.id} 
                           className={`group grid grid-cols-[auto_1fr_auto] items-center gap-4 px-2 md:px-4 py-3 hover:bg-white/10 rounded-lg transition-colors cursor-pointer ${isActive ? 'bg-white/5' : ''}`}
                           onClick={() => {
                             if (isActive) {
                               isPlaying ? pause() : resume();
                             } else if (onPlayTrack) {
                               onPlayTrack(track, tracks);
                             }
                           }}
                         >
                           <div className={`w-8 text-center font-medium ${isActive ? 'text-yellow-500' : 'text-neutral-400 group-hover:text-white'}`}>
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
                           
                           <div className="flex items-center gap-4 min-w-0">
                             {track.cover_url && (
                               <img src={track.cover_url} alt="" className="w-10 h-10 md:w-12 md:h-12 rounded object-cover shadow-sm shrink-0" />
                             )}
                             <div className="truncate">
                               <p className={`font-semibold truncate transition-colors text-sm md:text-base ${isActive ? 'text-yellow-500' : 'text-white group-hover:text-blue-400'}`}>
                                 {track.title}
                               </p>
                               <p className="text-xs md:text-sm text-neutral-400 truncate mt-0.5">
                                 {track.artist} 
                                 {track.explicit && <span className="inline-flex items-center justify-center px-1 rounded text-[9px] font-bold bg-neutral-600 text-white ml-2 align-middle uppercase tracking-widest">E</span>}
                               </p>
                             </div>
                           </div>
                           
                           <div className={`w-24 text-right text-sm font-medium flex items-center justify-end gap-3 md:gap-4 ${isActive ? 'text-yellow-500/80' : 'text-neutral-400'}`}>
                           <button
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
                                 cover_url: track.cover_url || (details && 'coverUrl' in details ? details.coverUrl : (details && 'cover_url' in details ? details.cover_url : undefined))
                               });
                             }}
                             className={`p-2 rounded-full transition-all hidden md:block ${
                               queue.some(t => t.id === track.id.toString() && (t.status === 'pending' || t.status === 'downloading'))
                                 ? "text-red-500 hover:bg-red-500/10" 
                                 : queue.some(t => t.id === track.id.toString() && t.status === 'completed')
                                 ? "text-green-500"
                                 : "opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10"
                             }`}
                             title="Download FLAC"
                           >
                             {queue.find(t => t.id === track.id.toString()) && (queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending') ? (
                               <X className="w-4 h-4" />
                             ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                               <Check className="w-4 h-4" />
                             ) : (
                               <Download className="w-4 h-4" />
                             )}
                           </button>
                             <span className="w-10 tabular-nums">{formatTime(track.duration)}</span>
                           </div>
                         </div>
                       );
                     })}
                   </div>
                 </div>
               </div>
             )}

             {/* Albums */}
             {albums && albums.length > 0 && (
               <div className="w-full mb-16">
                 <h2 className="text-2xl font-bold text-white mb-6">Albums</h2>
                <div className="flex overflow-x-auto gap-12 pb-6 custom-scrollbar snap-x after:content-[''] after:min-w-[160px] after:block">
                   {albums.map((album: any) => (
                      <div key={album.id} className="min-w-[288px] w-[288px] shrink-0 snap-start">
                        <VinylAlbumCard 
                          onClick={() => onOpenDetail && onOpenDetail('album', album)}
                          title={album.title} 
                          artist={album.artist} 
                          year={album.release_date ? album.release_date.split('-')[0] : 'Unknown'} 
                          releaseType="Album" 
                          coverImage={album.cover_url || 'https://upload.wikimedia.org/wikipedia/commons/c/c9/Vinyl_record.svg'} 
                        />
                      </div>
                   ))}
                 </div>
               </div>
             )}

             {/* EPs & Singles */}
             {eps_singles && eps_singles.length > 0 && (
               <div className="w-full mb-16">
                 <h2 className="text-2xl font-bold text-white mb-6">EP & Singles</h2>
                 <div className="flex overflow-x-auto gap-6 pb-6 custom-scrollbar snap-x after:content-[''] after:min-w-[40px] after:block">
                   {eps_singles.map((ep: any) => (
                      <div key={ep.id} className="min-w-[300px] w-[300px] shrink-0 snap-start">
                        <VinylAlbumCard 
                          animated={false}
                          onClick={() => onOpenDetail && onOpenDetail('album', ep)}
                          title={ep.title} 
                          artist={ep.artist} 
                          year={ep.release_date ? ep.release_date.split('-')[0] : 'Unknown'} 
                          releaseType="Single" 
                          coverImage={ep.cover_url || 'https://upload.wikimedia.org/wikipedia/commons/c/c9/Vinyl_record.svg'} 
                        />
                      </div>
                   ))}
                 </div>
               </div>
             )}

          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex animate-in fade-in duration-300">
      {/* Background layer with blurred cover image */}
      <div className="absolute inset-0 bg-neutral-950">
        {details?.coverUrl && (
          <div 
            className="absolute inset-0 opacity-40 bg-cover bg-center"
            style={{ 
              backgroundImage: `url(${details.coverUrl})`,
              filter: 'brightness(1.2) saturate(1.5) blur(80px)',
              transform: 'scale(1.1)' 
            }}
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/60 to-black/95" />
      </div>

      {/* Main Content Layout */}
      <div className="relative w-full h-full flex flex-col md:flex-row overflow-hidden">
        
        {/* Close button (top right) */}
        <button 
          onClick={onClose}
          className="absolute top-6 right-6 z-50 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white backdrop-blur-md transition-colors border border-white/10"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Left Side: Info Pane */}
        <div className="w-full md:w-1/3 lg:w-[450px] p-8 md:p-12 pb-32 flex flex-col md:h-full overflow-y-auto z-10 shrink-0 custom-scrollbar">
          <div className="mt-8 md:mt-12 flex flex-col items-center md:items-start text-center md:text-left">
            <div className="relative w-64 h-64 md:w-full md:h-auto md:aspect-square rounded-xl overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.5)] mb-8 group shrink-0">
              {details?.coverUrl ? (
                <img src={details.coverUrl} alt="Cover" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
              ) : (
                <div className="w-full h-full bg-neutral-800 animate-pulse" />
              )}
              {/* Play overlay on cover */}
              <div 
                className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center cursor-pointer"
                onClick={handleGlobalPlay}
              >
                <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center pl-1 hover:bg-white/30 transition-colors shadow-lg">
                  {isThisAlbumActive && isPlaying ? (
                    <Pause className="w-8 h-8 text-white fill-white drop-shadow-md -ml-1" />
                  ) : (
                    <Play className="w-8 h-8 text-white fill-white drop-shadow-md" />
                  )}
                </div>
              </div>
            </div>

            <h1 className="text-3xl md:text-5xl font-bold text-white mb-2 tracking-tight drop-shadow-sm leading-tight">
              {details?.title || "Loading..."}
            </h1>
            
            <div className="flex flex-col gap-3 justify-center md:justify-start mb-8 text-sm md:text-base">
              {/* Original preferred design */}
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 text-neutral-300 font-medium">
                <span>{details?.creator}</span>
                <span className="w-1 h-1 rounded-full bg-neutral-500" />
                <span className="capitalize">{type}</span>
                <span className="w-1 h-1 rounded-full bg-neutral-500" />
                <span>{details?.info}</span>
              </div>
              
              {/* Tracks & Duration added below */}
              {!isLoading && tracks.length > 0 && (
                <div className="flex items-center justify-center md:justify-start text-neutral-400 text-xs md:text-sm font-semibold tracking-wider">
                  {tracks.length} TRACKS ({formatTotalDuration(tracks.reduce((acc, t) => acc + t.duration, 0))})
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 items-center w-full justify-center md:justify-start">
              <button 
                className="flex-1 max-w-[160px] h-12 bg-white hover:bg-neutral-200 text-black rounded-full font-bold flex items-center justify-center gap-2 transition-transform active:scale-95 shadow-lg"
                onClick={handleGlobalPlay}
              >
                {isThisAlbumActive && isPlaying ? (
                  <>
                    <Pause className="w-5 h-5 fill-black" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 fill-black" />
                    Play
                  </>
                )}
              </button>
                             <div className="flex flex-1 items-center gap-2 max-w-[220px]">
                 <button 
                   onClick={handleDownloadAll}
                   disabled={!!queuedCollection && queuedCollection.status !== 'error' && queuedCollection.status !== 'cancelled'}
                   className={`flex-1 h-12 rounded-full font-bold flex items-center justify-center gap-2 transition-all active:scale-95 border relative overflow-hidden ${
                     queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')
                       ? "bg-blue-500/10 text-blue-400 border-blue-500/20" 
                       : queuedCollection?.status === 'completed'
                       ? "bg-green-500/10 text-green-400 border-green-500/20"
                       : "bg-white/10 hover:bg-white/20 text-white border-white/10"
                   }`}
                 >
                   {queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') && (
                     <div className="absolute inset-0 bg-blue-500/10 animate-pulse" />
                   )}
                   <Download className={`w-5 h-5 z-10 ${queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') ? 'animate-bounce' : ''}`} />
                   <span className="z-10">
                     {queuedCollection 
                       ? (queuedCollection.status === 'downloading' ? `Downloading...` : 
                          queuedCollection.status === 'pending' ? 'Queued' : 
                          queuedCollection.status === 'completed' ? 'Downloaded' : 'Download') 
                       : 'Download'}
                   </span>
                 </button>
                 {queuedCollection && (queuedCollection.status === 'downloading' || queuedCollection.status === 'pending') && (
                   <button
                     onClick={(e) => { e.stopPropagation(); cancelDownload(queuedCollection.id); }}
                     className="h-12 w-12 rounded-full flex shrink-0 items-center justify-center border border-white/10 bg-white/5 hover:bg-red-500/20 hover:text-red-500 hover:border-red-500/30 transition-all"
                     title="Cancel Download"
                   >
                     <X className="w-5 h-5" />
                   </button>
                 )}
               </div>
            </div>
          </div>
        </div>

        {/* Right Side: Tracklist */}
        <div className="flex-1 p-4 md:p-12 md:pl-0 h-full overflow-y-auto custom-scrollbar pb-32 z-10">
          <div className="w-full max-w-5xl mx-auto md:mt-12 bg-black/20 backdrop-blur-sm rounded-2xl border border-white/5 p-4 md:p-6 shadow-2xl">
            
            {/* Header row */}
            <div className="hidden md:grid grid-cols-[auto_1fr_auto] gap-4 px-4 py-3 border-b border-neutral-700/50 text-xs font-semibold tracking-widest text-neutral-400 mb-2">
              <div className="w-8 text-center">#</div>
              <div>TITLE</div>
              <div className="w-16 text-right">TIME</div>
            </div>

            {/* Tracks */}
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(10)].map((_, i) => (
                  <div key={i} className="h-16 w-full bg-white/5 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : tracks.length > 0 ? (
              <div className="space-y-1">
                {tracks.map((track, i) => {
                  const isActive = currentTrackId === track.id.toString();
                  return (
                    <div 
                      key={track.id} 
                      className={`group grid grid-cols-[auto_1fr_auto] items-center gap-4 px-2 md:px-4 py-3 hover:bg-white/10 rounded-lg transition-colors cursor-pointer ${isActive ? 'bg-white/5' : ''}`}
                      onClick={() => {
                        if (isActive) {
                          isPlaying ? pause() : resume();
                        } else if (onPlayTrack) {
                          onPlayTrack(track, tracks);
                        }
                      }}
                    >
                      <div className={`w-8 text-center font-medium ${isActive ? 'text-yellow-500' : 'text-neutral-400 group-hover:text-white'}`}>
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
                            <span className="block group-hover:hidden">{track.track_number || i + 1}</span>
                            <Play className="w-4 h-4 hidden group-hover:block mx-auto fill-current" />
                          </>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 min-w-0">
                        {track.cover_url && type === 'playlist' && (
                          <img src={track.cover_url} alt="" className="w-10 h-10 md:w-12 md:h-12 rounded object-cover shadow-sm shrink-0" />
                        )}
                        <div className="truncate">
                          <p className={`font-semibold truncate transition-colors text-sm md:text-base ${isActive ? 'text-yellow-500' : 'text-white group-hover:text-blue-400'}`}>
                            {track.title}
                          </p>
                          <p className="text-xs md:text-sm text-neutral-400 truncate mt-0.5">
                            {track.artist} 
                            {track.explicit && <span className="inline-flex items-center justify-center px-1 rounded text-[9px] font-bold bg-neutral-600 text-white ml-2 align-middle uppercase tracking-widest">E</span>}
                          </p>
                        </div>
                      </div>
                      
                      <div className={`w-24 text-right text-sm font-medium flex items-center justify-end gap-3 md:gap-4 ${isActive ? 'text-yellow-500/80' : 'text-neutral-400'}`}>
                           <button
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
                                 cover_url: track.cover_url || (details && 'coverUrl' in details ? details.coverUrl : (details && 'cover_url' in details ? details.cover_url : undefined))
                               });
                             }}
                             className={`p-2 rounded-full transition-all hidden md:block ${
                               queue.some(t => t.id === track.id.toString() && (t.status === 'pending' || t.status === 'downloading'))
                                 ? "text-red-500 hover:bg-red-500/10" 
                                 : queue.some(t => t.id === track.id.toString() && t.status === 'completed')
                                 ? "text-green-500"
                                 : "opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10"
                             }`}
                             title="Download FLAC"
                           >
                             {queue.find(t => t.id === track.id.toString()) && (queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending') ? (
                               <X className="w-4 h-4" />
                             ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                               <Check className="w-4 h-4" />
                             ) : (
                               <Download className="w-4 h-4" />
                             )}
                           </button>
                        <span className="w-10 tabular-nums">{formatTime(track.duration)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-24 text-neutral-500">
                <p className="text-lg">No tracks found.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
