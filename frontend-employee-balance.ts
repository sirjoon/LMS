import { useQuery } from 'react-query'
import { api } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'

interface LeaveBalance {
  leave_type_id: number
  leave_type_name: string
  remaining_days: number
}

function LeaveBalance() {
  const { data: balances, isLoading, error } = useQuery<LeaveBalance[]>(
    'employee-balance',
    async () => {
      const response = await api.get('/employee/balance')
      return response.data
    }
  )

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Failed to load leave balances</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Leave Balance</h1>
        <p className="mt-1 text-sm text-gray-600">
          Your current leave balance across all leave types
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {balances?.map((balance) => (
          <div key={balance.leave_type_id} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  {balance.leave_type_name}
                </h3>
                <p className="text-sm text-gray-500">Available days</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary-600">
                  {balance.remaining_days}
                </div>
                <p className="text-sm text-gray-500">days</p>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    balance.remaining_days > 10
                      ? 'bg-green-500'
                      : balance.remaining_days > 5
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{
                    width: `${Math.min(100, (balance.remaining_days / 20) * 100)}%`,
                  }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {balances?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No leave balances found</p>
        </div>
      )}
    </div>
  )
}

export default LeaveBalance