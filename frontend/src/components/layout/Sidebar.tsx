import { Link, useLocation } from "react-router-dom";
import { Home, Search, Download, Settings } from "lucide-react";

export default function Sidebar() {
  const location = useLocation();

  const navItems = [
    { name: "Home", path: "/", icon: <Home className="w-5 h-5" /> },
    { name: "Search", path: "/search", icon: <Search className="w-5 h-5" /> },
    { name: "Downloads", path: "/downloads", icon: <Download className="w-5 h-5" /> },
  ];

  return (
    <aside className="w-64 bg-black border-r border-neutral-800 flex flex-col h-full">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">SoundHaven</h1>
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                isActive
                  ? "bg-neutral-800 text-white font-medium"
                  : "text-neutral-400 hover:text-white hover:bg-neutral-900"
              }`}
            >
              {item.icon}
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 mt-auto">
        <Link
          to="/admin"
          className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
            location.pathname === "/admin"
              ? "bg-neutral-800 text-white font-medium"
              : "text-neutral-400 hover:text-white hover:bg-neutral-900"
          }`}
        >
          <Settings className="w-5 h-5" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
