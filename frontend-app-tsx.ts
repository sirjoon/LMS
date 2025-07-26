import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import AdminUsers from './pages/admin/Users'
import AdminLeaveTypes from './pages/admin/LeaveTypes'
import AdminHolidays from './pages/admin/Holidays'
import ManagerPending from './pages/manager/PendingRequests'
import ManagerHistory from './pages/manager/RequestHistory'
import EmployeeApply from './pages/employee/ApplyLeave'
import EmployeeBalance from './pages/employee/LeaveBalance'
import EmployeeRequests from './pages/employee/RequestHistory'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return <Login />
  }

  return (
    <Layout>
      <Routes>
        {/* Admin Routes */}
        {user.role === 'ADMIN' && (
          <>
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/leave-types" element={<AdminLeaveTypes />} />
            <Route path="/admin/holidays" element={<AdminHolidays />} />
            <Route path="/" element={<Navigate to="/admin/users" replace />} />
          </>
        )}

        {/* Manager Routes */}
        {user.role === 'MANAGER' && (
          <>
            <Route path="/manager/requests/pending" element={<ManagerPending />} />
            <Route path="/manager/requests/history" element={<ManagerHistory />} />
            <Route path="/" element={<Navigate to="/manager/requests/pending" replace />} />
          </>
        )}

        {/* Employee Routes */}
        {user.role === 'EMPLOYEE' && (
          <>
            <Route path="/employee/apply" element={<EmployeeApply />} />
            <Route path="/employee/balance" element={<EmployeeBalance />} />
            <Route path="/employee/requests" element={<EmployeeRequests />} />
            <Route path="/" element={<Navigate to="/employee/balance" replace />} />
          </>
        )}

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App