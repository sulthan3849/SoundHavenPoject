import MusicArtwork from "@/components/ui/music-artwork";

export default function PlaylistsDemoPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background dark px-4 relative overflow-hidden">
      <div className="text-center space-y-12 relative z-10">
        <div className="space-y-4">
          <div className="text-white mb-8">
            <h1 className="text-3xl font-bold mb-2">Playlist UI Preview</h1>
            <p className="text-neutral-400">Hover the cover or click to play</p>
          </div>
          <div>
            <div className="flex items-center justify-center">
              <MusicArtwork
                artist="Drake"
                music="Search & Rescue"
                albumArt="https://a5.mzstatic.com/us/r1000/0/Music116/v4/f9/6d/dc/f96ddc30-396d-6dbb-86fe-399831a26446/23UMGIM39822.rgb.jpg"
                isSong={true}
                isLoading={false}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
