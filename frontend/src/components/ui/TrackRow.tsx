import { Play, Pause, Download } from "lucide-react";
import { usePlayerStore } from "@/store/usePlayerStore";
import { useDownloadStore } from "@/store/useDownloadStore";

interface TrackRowProps {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: string;
  coverArt: string;
  index: number;
}

export default function TrackRow({ id, title, artist, album, duration, coverArt, index }: TrackRowProps) {
  const { currentTrackId, isPlaying, playTrack, pause, resume } = usePlayerStore();
  const { addDownload, queue } = useDownloadStore();

  const isThisTrackPlaying = currentTrackId === id && isPlaying;
  const isDownloading = queue.some(t => t.id === id);

  const handlePlay = () => {
    if (currentTrackId === id) {
      if (isPlaying) pause();
      else resume();
    } else {
      playTrack(id);
    }
  };

  const handleDownload = () => {
    if (isDownloading) return;
    addDownload({
      id,
      type: 'track',
      title,
      artist
    });
  };

  return (
    <div className="group flex items-center gap-4 px-4 py-3 rounded-md hover:bg-neutral-800/50 transition-colors">
      {/* Number / Play Button */}
      <div className="w-8 flex justify-center text-neutral-500 font-medium">
        <button 
          onClick={handlePlay}
          className={`
            hidden group-hover:flex items-center justify-center 
            ${isThisTrackPlaying ? 'text-white' : 'text-white'}
          `}
        >
          {isThisTrackPlaying ? (
            <Pause className="w-4 h-4 fill-current" />
          ) : (
            <Play className="w-4 h-4 fill-current" />
          )}
        </button>
        <span className={`group-hover:hidden ${isThisTrackPlaying ? 'text-green-500' : ''}`}>
          {index}
        </span>
      </div>

      {/* Title & Artist & Cover */}
      <div className="flex items-center gap-3 flex-1">
        <img src={coverArt} alt={title} className="w-10 h-10 rounded shadow-sm object-cover" />
        <div className="flex flex-col">
          <span className={`font-medium ${isThisTrackPlaying ? 'text-green-500' : 'text-white'}`}>
            {title}
          </span>
          <span className="text-sm text-neutral-400 hover:underline cursor-pointer">
            {artist}
          </span>
        </div>
      </div>

      {/* Album */}
      <div className="flex-1 text-sm text-neutral-400 hidden md:block hover:underline cursor-pointer">
        {album}
      </div>

      {/* Actions & Duration */}
      <div className="flex items-center gap-6">
        <button 
          onClick={handleDownload}
          disabled={isDownloading}
          className={`opacity-0 group-hover:opacity-100 transition-opacity ${
            isDownloading ? 'text-green-500 opacity-100' : 'text-neutral-400 hover:text-white'
          }`}
          title={isDownloading ? "Added to queue" : "Download FLAC"}
        >
          <Download className={`w-5 h-5 ${isDownloading ? 'animate-pulse' : ''}`} />
        </button>
        <span className="text-sm text-neutral-400 w-10 text-right">
          {duration}
        </span>
      </div>
    </div>
  );
}
