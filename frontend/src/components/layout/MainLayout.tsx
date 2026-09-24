import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import BottomPlayerBar from "./BottomPlayerBar";
import { usePlayerStore } from "@/store/usePlayerStore";

export default function MainLayout() {
  const { currentTrackId } = usePlayerStore();

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans text-foreground">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative overflow-hidden bg-background">
        <main className="flex-1 overflow-y-auto relative">
          <Outlet />
        </main>
      </div>

      {/* Persistent Bottom Player */}
      {currentTrackId && (
        <div className="absolute bottom-0 left-0 w-full z-50">
          <BottomPlayerBar />
        </div>
      )}
    </div>
  );
}
