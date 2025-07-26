import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useForm } from 'react-hook-form'
import { api } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
import toast from 'react-hot-toast'

interface LeaveType {
  id: number
  name: string
  default_quota: number
}

interface CreateLeaveTypeForm {
  name: string
  default_quota: number
}

function LeaveTypes() {
  const queryClient = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)

  const { data: leaveTypes, isLoading } = useQuery<LeaveType[]>(
    'admin-leave-types',
    async () => {
      const response = await api.get('/leave-types')
      return response.data
    }
  )

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateLeaveTypeForm>()

  const createLeaveTypeMutation = useMutation(
    async (data: CreateLeaveTypeForm) => {
      const response = await api.post('/admin/leave-types', data)
      return response.data
    },
    {
      onSuccess: () => {
        toast.success('Leave type created successfully')
        queryClient.invalidateQueries('admin-leave-types')
        queryClient.invalidateQueries('leave-types')
        reset()
        setShowCreateForm(false)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create leave type')
      },
    }
  )

  const onSubmit = (data: CreateLeaveTypeForm) => {
    createLeaveTypeMutation.mutate({
      ...data,
      default_quota: Number(data.default_quota),
    })
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
          <h1 className="text-2xl font-bold text-gray-900">Leave Types</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage leave categories and default quotas
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Add Leave Type'}
        </button>
      </div>

      {showCreateForm && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Leave Type</h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Leave Type Name *
                </label>
                <input
                  {...register('name', { required: 'Leave type name is required' })}
                  type="text"
                  id="name"
                  className="input mt-1"
                  placeholder="e.g., Vacation, Sick Leave"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="default_quota" className="block text-sm font-medium text-gray-700">
                  Default Quota (days) *
                </label>
                <input
                  {...register('default_quota', { 
                    required: 'Default quota is required',
                    min: { value: 0, message: 'Quota must be 0 or greater' },
                  })}
                  type="number"
                  id="default_quota"
                  min="0"
                  className="input mt-1"
                  placeholder="15"
                />
                {errors.default_quota && (
                  <p className="mt-1 text-sm text-red-600">{errors.default_quota.message}</p>
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
                disabled={createLeaveTypeMutation.isLoading}
                className="btn btn-primary"
              >
                {createLeaveTypeMutation.isLoading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  'Create Leave Type'
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {leaveTypes?.map((leaveType) => (
          <div key={leaveType.id} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  {leaveType.name}
                </h3>
                <p className="text-sm text-gray-500">Default quota</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-primary-600">
                  {leaveType.default_quota}
                </div>
                <p className="text-sm text-gray-500">days</p>
              </div>
            </div>
            
            <div className="mt-4 flex justify-end">
              <button className="text-sm text-primary-600 hover:text-primary-900">
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>

      {leaveTypes?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No leave types configured</p>
        </div>
      )}
    </div>
  )
}

export default LeaveTypes