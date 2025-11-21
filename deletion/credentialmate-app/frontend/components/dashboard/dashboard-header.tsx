"use client"

import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import { LogOut, User } from "lucide-react"

/**
 * Dashboard header component with user info and logout button.
 *
 * Displays the current user's name and email, and provides a logout button.
 * Used across all dashboard pages for consistent header UI.
 */
export function DashboardHeader() {
  const { user, logout } = useAuth()

  return (
    <div className="flex items-center justify-between mb-6 pb-4 border-b">
      <div className="flex items-center gap-3">
        <User className="h-5 w-5 text-muted-foreground" />
        <div>
          <p className="text-sm font-medium">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-xs text-muted-foreground">{user?.email}</p>
        </div>
      </div>
      <Button
        variant="outline"
        onClick={logout}
        aria-label="Logout"
        className="flex items-center gap-2"
      >
        <LogOut className="h-4 w-4" />
        Logout
      </Button>
    </div>
  )
}
