import { useMutation, useQuery, useQueryClient } from 'react-query'
import { api } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

interface LeaveRequest {
  id: number
  employee_name: string
  employee_email: string
  leave_type_name: string
  start_date: string
  end_date: string
  days_requested: number
  status: string
  notes?: string
  requested_at: string
}

function PendingRequests() {
  const queryClient = useQueryClient()

  const { data: requests, isLoading } = useQuery<LeaveRequest[]>(
    'manager-pending-requests',
    async () => {
      const response = await api.get('/manager/requests/pending')
      return response.data
    }
  )

  const approveMutation = useMutation(
    async (requestId: number) => {
      const response = await api.post(`/manager/requests/${requestId}/approve`)
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success('Leave request approved successfully')
        queryClient.invalidateQueries('manager-pending-requests')
        queryClient.invalidateQueries('manager-request-history')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to approve request')
      },
    }
  )

  const rejectMutation = useMutation(
    async (requestId: number) => {
      const response = await api.post(`/manager/requests/${requestId}/reject`)
      return response.data
    },
    {
      onSuccess: () => {
        toast.success('Leave request rejected')
        queryClient.invalidateQueries('manager-pending-requests')
        queryClient.invalidateQueries('manager-request-history')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to reject request')
      },
    }
  )

  const handleApprove = (requestId: number) => {
    if (window.confirm('Are you sure you want to approve this leave request?')) {
      approveMutation.mutate(requestId)
    }
  }

  const handleReject = (requestId: number) => {
    if (window.confirm('Are you sure you want to reject this leave request?')) {
      rejectMutation.mutate(requestId)
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
        <h1 className="text-2xl font-bold text-gray-900">Pending Leave Requests</h1>
        <p className="mt-1 text-sm text-gray-600">
          Review and approve leave requests from your team
        </p>
      </div>

      {requests?.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No pending leave requests</p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests?.map((request) => (
            <div key={request.id} className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {request.employee_name}
                  </h3>
                  <p className="text-sm text-gray-500">{request.employee_email}</p>
                </div>
                <div className="text-right">
                  <span className="badge badge-pending">Pending</span>
                  <p className="text-xs text-gray-500 mt-1">
                    Requested {format(new Date(request.requested_at), 'MMM d, yyyy')}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm font-medium text-gray-700">Leave Type</p>
                  <p className="text-sm text-gray-900">{request.leave_type_name}</p>
                </div>
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
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700">Notes</p>
                  <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded-md">
                    {request.notes}
                  </p>
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => handleReject(request.id)}
                  disabled={rejectMutation.isLoading}
                  className="btn btn-danger"
                >
                  {rejectMutation.isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    'Reject'
                  )}
                </button>
                <button
                  onClick={() => handleApprove(request.id)}
                  disabled={approveMutation.isLoading}
                  className="btn btn-success"
                >
                  {approveMutation.isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    'Approve'
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default PendingRequests