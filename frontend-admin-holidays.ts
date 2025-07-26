import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useForm } from 'react-hook-form'
import { api } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

interface Holiday {
  id: number
  date: string
  description: string
}

interface CreateHolidayForm {
  date: string
  description: string
}

function Holidays() {
  const queryClient = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)

  const { data: holidays, isLoading } = useQuery<Holiday[]>(
    'admin-holidays',
    async () => {
      const response = await api.get('/holidays')
      return response.data
    }
  )

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateHolidayForm>()

  const createHolidayMutation = useMutation(
    async (data: CreateHolidayForm) => {
      const response = await api.post('/admin/holidays', data)
      return response.data
    },
    {
      onSuccess: () => {
        toast.success('Holiday created successfully')
        queryClient.invalidateQueries('admin-holidays')
        queryClient.invalidateQueries('holidays')
        reset()
        setShowCreateForm(false)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create holiday')
      },
    }
  )

  const onSubmit = (data: CreateHolidayForm) => {
    createHolidayMutation.mutate(data)
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Corporate Holidays</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage company holidays and blackout dates
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Add Holiday'}
        </button>
      </div>

      {showCreateForm && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Holiday</h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="date" className="block text-sm font-medium text-gray-700">
                  Date *
                </label>
                <input
                  {...register('date', { required: 'Date is required' })}
                  type="date"
                  id="date"
                  className="input mt-1"
                />
                {errors.date && (
                  <p className="mt-1 text-sm text-red-600">{errors.date.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description *
                </label>
                <input
                  {...register('description', { required: 'Description is required' })}
                  type="text"
                  id="description"
                  className="input mt-1"
                  placeholder="e.g., Christmas Day"
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createHolidayMutation.isLoading}
                className="btn btn-primary"
              >
                {createHolidayMutation.isLoading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  'Create Holiday'
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Holiday
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Day of Week
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {holidays?.map((holiday) => {
                const holidayDate = new Date(holiday.date)
                return (
                  <tr key={holiday.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {format(holidayDate, 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {holiday.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {format(holidayDate, 'EEEE')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-primary-600 hover:text-primary-900 mr-4">
                        Edit
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        Delete
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {holidays?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No holidays configured</p>
        </div>
      )}
    </div>
  )
}

export default Holidays