import { useEffect, useRef, useState } from "react";
import { Play, Pause, SkipBack, SkipForward, Volume2 } from "lucide-react";
import { usePlayerStore } from "@/store/usePlayerStore";

const DraggableSlider = ({ 
  value, 
  onChange, 
  onDragStart, 
  onDragEnd, 
  className 
}: { 
  value: number, 
  onChange: (v: number) => void, 
  onDragStart?: () => void, 
  onDragEnd?: (v: number) => void, 
  className?: string 
}) => {
  const barRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragValue, setDragValue] = useState(value);

  useEffect(() => {
    if (!isDragging) {
      setDragValue(value);
    }
  }, [value, isDragging]);
  
  const handlePointerDown = (e: React.PointerEvent) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    setIsDragging(true);
    onDragStart?.();
    updateValue(e.clientX);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (isDragging && e.currentTarget.hasPointerCapture(e.pointerId)) {
      updateValue(e.clientX);
    }
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    e.currentTarget.releasePointerCapture(e.pointerId);
    if (isDragging) {
      setIsDragging(false);
      onDragEnd?.(dragValue);
    }
  };

  const updateValue = (clientX: number) => {
    if (!barRef.current) return;
    const rect = barRef.current.getBoundingClientRect();
    const pos = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    setDragValue(pos);
    onChange(pos);
  };

  const displayValue = isDragging ? dragValue : value;

  return (
    <div 
      className={`relative h-1.5 bg-neutral-800 rounded-full cursor-pointer group flex items-center touch-none ${className}`}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      ref={barRef}
    >
      <div 
        className="absolute left-0 top-0 bottom-0 bg-white rounded-full group-hover:bg-yellow-500 transition-colors pointer-events-none" 
        style={{ width: `${displayValue * 100}%` }}
      />
      <div 
        className={`absolute w-3 h-3 bg-white rounded-full pointer-events-none shadow-md transition-opacity ${isDragging ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}
        style={{ left: `calc(${displayValue * 100}% - 6px)` }}
      />
    </div>
  );
};

export default function BottomPlayerBar() {
  const { currentTrack, isPlaying, pause, resume, playNext, playPrev } = usePlayerStore();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isDraggingProgress, setIsDraggingProgress] = useState(false);

  // Sync isPlaying and Volume state with HTMLAudioElement
  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(console.error);
      } else {
        audioRef.current.pause();
      }
      audioRef.current.volume = volume;
    }
  }, [isPlaying, currentTrack, volume]);

  // Handle time update for progress bar
  const handleTimeUpdate = () => {
    if (audioRef.current && !isDraggingProgress) {
      setProgress(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  // Handle drag end for progress bar
  const handleProgressDragEnd = (newPercent: number) => {
    if (audioRef.current && duration) {
      const newTime = newPercent * duration;
      audioRef.current.currentTime = newTime;
      setProgress(newTime);
    }
    setIsDraggingProgress(false);
  };

  // Format time (mm:ss)
  const formatTime = (time: number) => {
    if (isNaN(time)) return "0:00";
    const m = Math.floor(time / 60);
    const s = Math.floor(time % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (!currentTrack) return null;

  const progressPercent = duration > 0 ? (progress / duration) * 100 : 0;

  return (
    <div className="h-24 bg-neutral-950/90 backdrop-blur-xl border-t border-white/10 px-6 flex items-center justify-between w-full shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
      {/* Hidden Audio Element */}
      <audio 
        ref={audioRef} 
        src={currentTrack.preview_url}
        onTimeUpdate={handleTimeUpdate}
        onEnded={playNext}
        onLoadedMetadata={handleTimeUpdate}
      />

      {/* Track Info */}
      <div className="flex items-center gap-4 w-1/3">
        <div className="w-14 h-14 bg-neutral-800 rounded-md overflow-hidden relative shadow-lg">
          {currentTrack.cover_url ? (
            <img src={currentTrack.cover_url} alt={currentTrack.title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-neutral-700 to-neutral-900" />
          )}
        </div>
        <div className="overflow-hidden">
          <h4 className="text-white text-sm font-medium truncate">{currentTrack.title}</h4>
          <p className="text-neutral-400 text-xs truncate">{currentTrack.artist}</p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col items-center gap-2 w-1/3">
        <div className="flex items-center gap-6">
          <button onClick={playPrev} className="text-neutral-400 hover:text-white transition-colors active:scale-95">
            <SkipBack className="w-5 h-5" />
          </button>
          <button
            onClick={isPlaying ? pause : resume}
            className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-black hover:scale-105 transition-transform shadow-lg active:scale-95"
          >
            {isPlaying ? (
              <Pause className="w-5 h-5 fill-current" />
            ) : (
              <Play className="w-5 h-5 fill-current ml-1" />
            )}
          </button>
          <button onClick={playNext} className="text-neutral-400 hover:text-white transition-colors active:scale-95">
            <SkipForward className="w-5 h-5" />
          </button>
        </div>
        {/* Progress Bar */}
        <div className="w-full flex items-center gap-3">
          <span className="text-[10px] font-medium text-neutral-400 w-8 text-right tabular-nums">
            {formatTime(progress)}
          </span>
          <DraggableSlider 
            className="flex-1"
            value={duration > 0 ? progress / duration : 0}
            onChange={(v) => {
              // We just update the local progress state for UI while dragging
              if (duration) setProgress(v * duration);
            }}
            onDragStart={() => setIsDraggingProgress(true)}
            onDragEnd={handleProgressDragEnd}
          />
          <span className="text-[10px] font-medium text-neutral-400 w-8 tabular-nums">
            {formatTime(duration)}
          </span>
        </div>
      </div>

      {/* Volume & Extra Controls */}
      <div className="flex items-center justify-end gap-4 w-1/3">
        <Volume2 className="w-5 h-5 text-neutral-400" />
        <DraggableSlider 
          className="w-24"
          value={volume}
          onChange={(v) => setVolume(v)}
        />
      </div>
    </div>
  );
}
