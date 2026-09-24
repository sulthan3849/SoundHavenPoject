import { useState } from "react";
import MusicArtwork from "@/components/ui/music-artwork";
import { GlassmorphismListenAppBlock } from "@/components/ui/glassmorphism-listen-app-block-shadcnui";
import TrackRow from "@/components/ui/TrackRow";
// Catatan: great-ui-vinyl-album-card.tsx masih tertanam di dalam glassmorphism-listen-app-block-shadcnui untuk sementara.
// Nanti akan diekstrak pada Task 4.

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState("all");

  const tabs = [
    { id: "all", label: "All" },
    { id: "tracks", label: "Tracks" },
    { id: "albums", label: "Albums" },
    { id: "playlists", label: "Playlists" },
    { id: "profiles", label: "Profiles" },
  ];

  return (
    <div className="space-y-8 pb-24">
      {/* Search Header */}
      <div className="sticky top-0 z-10 bg-neutral-950/80 backdrop-blur-md pb-4 pt-2 -mt-2">
        <input
          type="text"
          placeholder="What do you want to listen to?"
          className="w-full max-w-2xl bg-neutral-900 border border-neutral-800 text-white rounded-full px-6 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-white/20 transition-shadow"
        />
        
        {/* Tabs */}
        <div className="flex gap-2 mt-6 overflow-x-auto pb-2 scrollbar-none">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-white text-black"
                  : "bg-neutral-900 text-white hover:bg-neutral-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="mt-8">
        {activeTab === "playlists" && (
          <div>
            <h3 className="text-xl font-bold mb-6 text-white">Playlists</h3>
            <div className="flex flex-wrap gap-12">
              <MusicArtwork
                artist="Drake"
                music="Search & Rescue"
                albumArt="https://a5.mzstatic.com/us/r1000/0/Music116/v4/f9/6d/dc/f96ddc30-396d-6dbb-86fe-399831a26446/23UMGIM39822.rgb.jpg"
                isSong={false}
              />
              <MusicArtwork
                artist="The Weeknd"
                music="Blinding Lights"
                albumArt="https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36"
                isSong={false}
              />
            </div>
          </div>
        )}

        {activeTab === "albums" && (
          <div>
            <h3 className="text-xl font-bold mb-6 text-white">Albums</h3>
            <div className="scale-75 origin-top-left">
               {/* Memanggil UI lama sementara sebagai demo album gradasi */}
               <GlassmorphismListenAppBlock />
            </div>
          </div>
        )}

        {activeTab === "tracks" && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Top Tracks</h3>
            </div>
            
            {/* Table Header */}
            <div className="flex items-center gap-4 px-4 py-2 border-b border-neutral-800 text-sm text-neutral-400 font-medium mb-4">
              <div className="w-8 text-center">#</div>
              <div className="flex-1">Title</div>
              <div className="flex-1 hidden md:block">Album</div>
              <div className="w-20 text-right">Time</div>
            </div>

            {/* Track List */}
            <div className="flex flex-col">
              <TrackRow 
                index={1}
                id="track-01"
                title="Search & Rescue"
                artist="Drake"
                album="Search & Rescue"
                duration="4:32"
                coverArt="https://a5.mzstatic.com/us/r1000/0/Music116/v4/f9/6d/dc/f96ddc30-396d-6dbb-86fe-399831a26446/23UMGIM39822.rgb.jpg"
              />
              <TrackRow 
                index={2}
                id="track-02"
                title="Blinding Lights"
                artist="The Weeknd"
                album="After Hours"
                duration="3:20"
                coverArt="https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36"
              />
              <TrackRow 
                index={3}
                id="track-03"
                title="Starboy"
                artist="The Weeknd, Daft Punk"
                album="Starboy"
                duration="3:50"
                coverArt="https://i.scdn.co/image/ab67616d0000b274a048415c345337500af7a7af"
              />
            </div>
          </div>
        )}

        {activeTab !== "playlists" && activeTab !== "albums" && activeTab !== "tracks" && (
          <div className="text-neutral-500 py-12 text-center border border-dashed border-neutral-800 rounded-lg">
            {activeTab} content will go here
          </div>
        )}
      </div>
    </div>
  );
}
