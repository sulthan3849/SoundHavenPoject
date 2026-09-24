import { useState, useEffect } from "react"
import { GlassmorphismListenAppBlock } from "@/components/ui/glassmorphism-listen-app-block-shadcnui"
import AdminPage from "@/pages/AdminPage"

export default function App() {
  const [currentHash, setCurrentHash] = useState(window.location.hash)

  useEffect(() => {
    const handleHashChange = () => {
      setCurrentHash(window.location.hash)
    }
    window.addEventListener("hashchange", handleHashChange)
    return () => window.removeEventListener("hashchange", handleHashChange)
  }, [])

  if (currentHash === "#admin") {
    return <AdminPage />
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background text-foreground dark">
      <GlassmorphismListenAppBlock />
    </main>
  )
}
