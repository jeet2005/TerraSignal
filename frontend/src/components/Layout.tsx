import { useEffect } from 'react'
import { Outlet, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useUIStore } from '../stores/uiStore'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { BottomSheet } from './BottomSheet'
import { AlertFeed } from './AlertFeed'
import { EventPopup } from './EventPopup'

export function Layout() {
  const { isAuthenticated, isLoading, refreshUser } = useAuthStore()
  const { sidebarOpen, isMobile, bottomSheetOpen, bottomSheetContent, setSidebarOpen } = useUIStore()
  const location = useLocation()
  const navigate = useNavigate()
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      refreshUser().catch(() => navigate('/login'))
    }
  }, [isAuthenticated, isLoading, refreshUser, navigate])
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-50 dark:bg-dark-950">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  const showSidebar = !isMobile || sidebarOpen
  const showBottomSheet = isMobile && (bottomSheetOpen || bottomSheetContent)
  
  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 flex flex-col">
      <Header />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Desktop Sidebar */}
        <aside
          className={cn(
            'fixed inset-y-0 left-0 z-30 lg:relative w-72 bg-white dark:bg-dark-950 border-r border-dark-200 dark:border-dark-800 transition-transform duration-300',
            showSidebar ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          )}
        >
          <Sidebar />
        </aside>
        
        {/* Mobile sidebar overlay */}
        {isMobile && sidebarOpen && (
          <div
            className="fixed inset-0 z-20 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
        )}
        
        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden lg:ml-0">
          <div className="flex-1 relative">
            <Outlet />
          </div>
          
          {/* Alert Feed / Timeline */}
          <AlertFeed />
        </main>
        
        {/* Mobile Bottom Sheet */}
        {showBottomSheet && (
          <BottomSheet
            content={bottomSheetContent}
            onClose={() => useUIStore.getState().setBottomSheetOpen(false)}
          />
        )}
        
        {/* Event Popup */}
        <EventPopup />
      </div>
    </div>
  )
}