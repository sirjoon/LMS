import { useQuery } from 'react-query'
import { api } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
import { format } from 'date-fns'

interface LeaveRequest {
  id: number
  leave_type_name: string
  start_date: string
  end_date: string
  days_requested: number
  status: string
  notes?: string
  requested_at: string
  decided_at?: string
  manager_name: string
}

function RequestHistory() {
  const { data: requests, isLoading } = useQuery<LeaveRequest[]>(
    'employee-requests',
    async () => {
      const response = await api.get('/employee/requests')
      return response.data
    }
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'badge-approved'
      case 'REJECTED':
        return 'badge-rejected'
      case 'PENDING':
        return 'badge-pending'
      case 'CANCELLED':
        return 'badge-cancelled'
      default:
        return 'badge-pending'
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Leave Requests</h1>
        <p className="mt-1 text-sm text-gray-600">
          History of all your leave requests
        </p>
      </div>

      {requests?.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No leave requests found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests?.map((request) => (
            <div key={request.id} className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {request.leave_type_name}
                  </h3>
                  <p className="text-sm text-gray-500">Manager: {request.manager_name}</p>
                </div>
                <div className="text-right">
                  <span className={`badge ${getStatusBadge(request.status)}`}>
                    {request.status}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {request.decided_at
                      ? `Decided ${format(new Date(request.decided_at), 'MMM d, yyyy')}`
                      : `Requested ${format(new Date(request.requested_at), 'MMM d, yyyy')}`}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-700">Duration</p>
                  <p className="text-sm text-gray-900">
                    {format(new Date(request.start_date), 'MMM d, yyyy')} - {' '}
                    {format(new Date(request.end_date), 'MMM d, yyyy')}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Days Requested</p>
                  <p className="text-sm text-gray-900">{request.days_requested} days</p>
                </div>
              </div>

              {request.notes && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700">Notes</p>
                  <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded-md">
                    {request.notes}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RequestHistory