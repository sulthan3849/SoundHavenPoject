import { useState, useEffect, useCallback } from "react";

const API_BASE = "http://localhost:8000";

interface AuthState {
  status: string;
  user_code: string | null;
  verification_url: string | null;
  error_message: string | null;
}

export default function AdminPage() {
  const [password, setPassword] = useState("");
  const [isAuthed, setIsAuthed] = useState(false);
  const [error, setError] = useState("");
  const [tidalConnected, setTidalConnected] = useState(false);
  const [desktopConnected, setDesktopConnected] = useState(false);
  const [authState, setAuthState] = useState<AuthState | null>(null);
  const [desktopAuthState, setDesktopAuthState] = useState<AuthState | null>(null);
  const [loading, setLoading] = useState(false);

  // Check if admin is already authed (stored in sessionStorage)
  useEffect(() => {
    const stored = sessionStorage.getItem("admin_password");
    if (stored) {
      setPassword(stored);
      setIsAuthed(true);
    }
  }, []);

  // Once admin is authenticated, check TIDAL connection status
  useEffect(() => {
    if (isAuthed) {
      checkTidalStatus();
    }
  }, [isAuthed]);

  // Poll for pending auth state
  useEffect(() => {
    if (!authState || authState.status !== "pending") return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/pending`);
        const data: AuthState = await res.json();
        setAuthState(data);

        if (data.status === "success") {
          setTidalConnected(true);
          clearInterval(interval);
        } else if (data.status === "error") {
          clearInterval(interval);
        }
      } catch {
        // ignore network errors during polling
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [authState?.status]);

  // Poll for pending desktop auth state
  useEffect(() => {
    if (!desktopAuthState || desktopAuthState.status !== "pending") return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/desktop/pending`);
        const data: AuthState = await res.json();
        setDesktopAuthState(data);

        if (data.status === "success") {
          setDesktopConnected(true);
          clearInterval(interval);
        } else if (data.status === "error") {
          clearInterval(interval);
        }
      } catch {
        // ignore network errors
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [desktopAuthState?.status]);

  const checkTidalStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/auth/status`);
      const data = await res.json();
      setTidalConnected(data.authenticated);
      setDesktopConnected(data.desktop_authenticated);
    } catch {
      setTidalConnected(false);
      setDesktopConnected(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/admin/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (res.ok) {
        sessionStorage.setItem("admin_password", password);
        setIsAuthed(true);
      } else {
        setError("Invalid password");
      }
    } catch {
      setError("Could not connect to server");
    } finally {
      setLoading(false);
    }
  };

  const handleTidalConnect = async () => {
    setLoading(true);
    setError("");
    setAuthState(null);

    try {
      const res = await fetch(`${API_BASE}/api/admin/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      const data = await res.json();

      if (res.ok) {
        setAuthState({
          status: "pending",
          user_code: data.user_code,
          verification_url: data.verification_url,
          error_message: null,
        });
      } else {
        setError(data.detail || "Failed to start login flow");
      }
    } catch {
      setError("Could not connect to server");
    } finally {
      setLoading(false);
    }
  };

  const handleTidalDisconnect = async () => {
    setLoading(true);

    try {
      await fetch(`${API_BASE}/api/admin/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      setTidalConnected(false);
      setDesktopConnected(false);
      setAuthState(null);
      setDesktopAuthState(null);
    } catch {
      setError("Failed to disconnect");
    } finally {
      setLoading(false);
    }
  };

  const handleDesktopConnect = async () => {
    setLoading(true);
    setError("");
    setDesktopAuthState(null);

    try {
      const res = await fetch(`${API_BASE}/api/admin/auth/desktop/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      const data = await res.json();

      if (res.ok) {
        setDesktopAuthState({
          status: "pending",
          user_code: data.user_code,
          verification_url: data.verification_url,
          error_message: null,
        });
      } else {
        setError(data.detail || "Failed to start desktop login flow");
      }
    } catch {
      setError("Could not connect to server");
    } finally {
      setLoading(false);
    }
  };

  const handleAdminLogout = () => {
    sessionStorage.removeItem("admin_password");
    setIsAuthed(false);
    setPassword("");
  };

  // â”€â”€â”€ Admin Login Screen â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  if (!isAuthed) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-full max-w-sm px-6">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              SoundHaven
            </h1>
            <p className="text-sm text-neutral-500 mt-1">Admin Access</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-full text-white placeholder-neutral-600 text-sm focus:outline-none focus:border-neutral-600 transition-colors"
              autoFocus
            />
            {error && (
              <p className="text-red-500 text-xs text-center">{error}</p>
            )}
            <button
              type="submit"
              disabled={loading || !password}
              className="w-full py-3 bg-white text-black font-semibold text-sm rounded-full hover:bg-neutral-200 transition-colors disabled:opacity-50"
            >
              {loading ? "Verifying..." : "Access Dashboard"}
            </button>
          </form>

          <p className="text-center mt-6">
            <a
              href="/"
              className="text-xs text-neutral-600 hover:text-neutral-400 transition-colors"
            >
              Back to SoundHaven
            </a>
          </p>
        </div>
      </div>
    );
  }

  // â”€â”€â”€ Admin Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-neutral-900 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold tracking-tight">
            SoundHaven Admin
          </h1>
          <p className="text-xs text-neutral-500">
            System Configuration & Account Management
          </p>
        </div>
        <div className="flex gap-3">
          <a
            href="/"
            className="px-4 py-2 text-xs text-neutral-400 border border-neutral-800 rounded-full hover:border-neutral-600 transition-colors"
          >
            Back to App
          </a>
          <button
            onClick={handleAdminLogout}
            className="px-4 py-2 text-xs text-neutral-400 border border-neutral-800 rounded-full hover:border-red-800 hover:text-red-400 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-6 py-10 space-y-8">
        {/* TIDAL Account Section */}
        <section className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider mb-4">
            TIDAL Account
          </h2>

          {/* Connection Status */}
          <div className="flex items-center justify-between mb-6 p-4 bg-neutral-900/50 rounded-xl">
            <div className="flex items-center gap-3">
              <div
                className={`w-2.5 h-2.5 rounded-full ${
                  tidalConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <div>
                <p className="text-sm font-medium text-white">
                  {tidalConnected ? "Connected" : "Not Connected"}
                </p>
                <p className="text-xs text-neutral-500">
                  {tidalConnected
                    ? "TIDAL account is linked and active"
                    : "Link your TIDAL account to enable search & downloads"}
                </p>
              </div>
            </div>
          </div>

          {/* Pending OAuth Flow */}
          {authState?.status === "pending" && (
            <div className="mb-6 p-5 bg-neutral-900 border border-neutral-800 rounded-xl text-center space-y-3">
              <p className="text-xs text-neutral-400 uppercase tracking-wider">
                Waiting for authorization
              </p>
              <div className="py-3">
                <p className="text-3xl font-mono font-bold text-white tracking-[0.3em]">
                  {authState.user_code}
                </p>
              </div>
              <p className="text-sm text-neutral-400">
                Open{" "}
                <a
                  href={authState.verification_url || "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 underline hover:text-blue-300"
                >
                  {authState.verification_url}
                </a>{" "}
                on your phone or browser
              </p>
              <p className="text-xs text-neutral-600">
                Log in to your TIDAL account and enter the code above
              </p>
              <div className="flex items-center justify-center gap-2 pt-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
                <span className="text-xs text-neutral-500">
                  Checking link...
                </span>
              </div>
            </div>
          )}

          {/* Success Message */}
          {authState?.status === "success" && (
            <div className="mb-6 p-4 bg-green-950/30 border border-green-900/50 rounded-xl text-center">
              <p className="text-sm text-green-400">
                TIDAL account successfully linked!
              </p>
            </div>
          )}

          {/* Error Message */}
          {authState?.status === "error" && (
            <div className="mb-6 p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-center">
              <p className="text-sm text-red-400">
                {authState.error_message || "Authorization failed."}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            {!tidalConnected ? (
              <button
                onClick={handleTidalConnect}
                disabled={loading || authState?.status === "pending"}
                className="flex-1 py-3 bg-white text-black font-semibold text-sm rounded-full hover:bg-neutral-200 transition-colors disabled:opacity-50"
              >
                {authState?.status === "pending"
                  ? "Waiting for authorization..."
                  : "Connect TIDAL TV (For Downloads)"}
              </button>
            ) : (
              <button
                onClick={handleTidalDisconnect}
                disabled={loading}
                className="flex-1 py-3 bg-neutral-900 text-red-400 font-semibold text-sm rounded-full border border-neutral-800 hover:border-red-800 transition-colors disabled:opacity-50"
              >
                Disconnect Account
              </button>
            )}
          </div>
        </section>

        {/* Desktop Account Section */}
        <section className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider mb-4">
            Secondary Search Authentication
          </h2>
          <p className="text-xs text-neutral-500 mb-6">
            A secondary Desktop Session is required to bypass API restrictions and allow searching for user-created playlists perfectly. 
            <strong> You only need to do this once.</strong>
          </p>

          {/* Connection Status */}
          <div className="flex items-center justify-between mb-6 p-4 bg-neutral-900/50 rounded-xl">
            <div className="flex items-center gap-3">
              <div
                className={`w-2.5 h-2.5 rounded-full ${
                  desktopConnected ? "bg-green-500" : "bg-yellow-500"
                }`}
              />
              <div>
                <p className="text-sm font-medium text-white">
                  {desktopConnected ? "Search Connected" : "Search Not Connected"}
                </p>
                <p className="text-xs text-neutral-500">
                  {desktopConnected
                    ? "Secondary Desktop Session is active for searches"
                    : "Connect this to enable User Playlists in search results"}
                </p>
              </div>
            </div>
          </div>

          {desktopConnected && (
            <button
              onClick={async () => {
                if (window.confirm("Disconnect Secondary Search Authentication?")) {
                  try {
                    const res = await fetch(`${API_BASE}/api/admin/auth/desktop/disconnect`, {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ password }),
                    });
                    if (res.ok) {
                      // Trigger re-check or state update
                      window.location.reload();
                    } else {
                      alert("Failed to disconnect Desktop session");
                    }
                  } catch (err) {
                    alert(String(err));
                  }
                }
              }}
              className="w-full py-3 px-4 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 rounded-xl transition-colors font-medium text-sm mb-6"
            >
              Disconnect Search Account
            </button>
          )}

          {/* Pending Desktop OAuth Flow */}
          {desktopAuthState?.status === "pending" && (
            <div className="mb-6 p-5 bg-neutral-900 border border-neutral-800 rounded-xl text-center space-y-3">
              <p className="text-xs text-neutral-400 uppercase tracking-wider">
                Waiting for authorization
              </p>
              <div className="py-3">
                <p className="text-3xl font-mono font-bold text-white tracking-[0.3em]">
                  {desktopAuthState.user_code}
                </p>
              </div>
              <p className="text-sm text-neutral-400">
                Open{" "}
                <a
                  href={desktopAuthState.verification_url || "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 underline hover:text-blue-300"
                >
                  {desktopAuthState.verification_url}
                </a>{" "}
                on your phone or browser
              </p>
              <p className="text-xs text-neutral-600">
                Log in to your TIDAL account and enter the code above
              </p>
              <div className="flex items-center justify-center gap-2 pt-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
                <span className="text-xs text-neutral-500">
                  Checking link...
                </span>
              </div>
            </div>
          )}

          {/* Success Message */}
          {desktopAuthState?.status === "success" && (
            <div className="mb-6 p-4 bg-green-950/30 border border-green-900/50 rounded-xl text-center">
              <p className="text-sm text-green-400">
                Secondary Search Session successfully linked!
              </p>
            </div>
          )}

          {/* Error Message */}
          {desktopAuthState?.status === "error" && (
            <div className="mb-6 p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-center">
              <p className="text-sm text-red-400">
                {desktopAuthState.error_message || "Authorization failed."}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            {!desktopConnected ? (
              <button
                onClick={handleDesktopConnect}
                disabled={loading || desktopAuthState?.status === "pending"}
                className="flex-1 py-3 bg-neutral-800 text-white font-semibold text-sm rounded-full hover:bg-neutral-700 transition-colors disabled:opacity-50"
              >
                {desktopAuthState?.status === "pending"
                  ? "Waiting for authorization..."
                  : "Connect Search Account (Desktop)"}
              </button>
            ) : null}
          </div>
        </section>

        {/* Server Info */}
        <section className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider mb-4">
            Server Information
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between py-2 border-b border-neutral-900">
              <span className="text-neutral-500">Backend</span>
              <span className="text-neutral-300 font-mono text-xs">
                FastAPI + OrpheusDL
              </span>
            </div>
            <div className="flex justify-between py-2 border-b border-neutral-900">
              <span className="text-neutral-500">API Endpoint</span>
              <span className="text-neutral-300 font-mono text-xs">
                {API_BASE}
              </span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-neutral-500">Audio Quality</span>
              <span className="text-neutral-300 font-mono text-xs text-yellow-500">
                MAX (Up to 24-bit / 192kHz)
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

