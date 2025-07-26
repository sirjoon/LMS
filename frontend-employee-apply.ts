import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from 'react-query'
import { api } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
import toast from 'react-hot-toast'

interface LeaveType {
  id: number
  name: string
  default_quota: number
}

interface ApplyLeaveForm {
  leave_type_id: number
  start_date: string
  end_date: string
  notes?: string
}

function ApplyLeave() {
  const queryClient = useQueryClient()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<ApplyLeaveForm>()

  // Watch dates to calculate duration
  const startDate = watch('start_date')
  const endDate = watch('end_date')

  // Fetch leave types
  const { data: leaveTypes, isLoading: loadingTypes } = useQuery<LeaveType[]>(
    'leave-types',
    async () => {
      const response = await api.get('/leave-types')
      return response.data
    }
  )

  // Submit leave request
  const submitMutation = useMutation(
    async (data: ApplyLeaveForm) => {
      const response = await api.post('/employee/requests', {
        ...data,
        leave_type_id: Number(data.leave_type_id),
      })
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(`Leave request submitted! Sent to ${data.manager_notified}`)
        reset()
        queryClient.invalidateQueries('employee-requests')
        queryClient.invalidateQueries('employee-balance')
      },
      onError: (error: any) => {
        const message = error.response?.data?.detail || 'Failed to submit leave request'
        toast.error(message)
      },
    }
  )

  const onSubmit = async (data: ApplyLeaveForm) => {
    setIsSubmitting(true)
    try {
      await submitMutation.mutateAsync(data)
    } finally {
      setIsSubmitting(false)
    }
  }

  const calculateDays = () => {
    if (!startDate || !endDate) return 0
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = end.getTime() - start.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  }

  if (loadingTypes) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Apply for Leave</h1>
        <p className="mt-1 text-sm text-gray-600">
          Submit a new leave request for manager approval
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
        <div>
          <label htmlFor="leave_type_id" className="block text-sm font-medium text-gray-700">
            Leave Type *
          </label>
          <select
            {...register('leave_type_id', { required: 'Please select a leave type' })}
            id="leave_type_id"
            className="input mt-1"
          >
            <option value="">Select leave type</option>
            {leaveTypes?.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
          {errors.leave_type_id && (
            <p className="mt-1 text-sm text-red-600">{errors.leave_type_id.message}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">
              Start Date *
            </label>
            <input
              {...register('start_date', { required: 'Start date is required' })}
              type="date"
              id="start_date"
              min={new Date().toISOString().split('T')[0]}
              className="input mt-1"
            />
            {errors.start_date && (
              <p className="mt-1 text-sm text-red-600">{errors.start_date.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">
              End Date *
            </label>
            <input
              {...register('end_date', { 
                required: 'End date is required',
                validate: (value) => {
                  if (startDate && value < startDate) {
                    return 'End date must be after start date'
                  }
                  return true
                }
              })}
              type="date"
              id="end_date"
              min={startDate || new Date().toISOString().split('T')[0]}
              className="input mt-1"
            />
            {errors.end_date && (
              <p className="mt-1 text-sm text-red-600">{errors.end_date.message}</p>
            )}
          </div>
        </div>

        {startDate && endDate && (
          <div className="p-3 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-700">
              <strong>Duration:</strong> {calculateDays()} days
            </p>
          </div>
        )}

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
            Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            id="notes"
            rows={4}
            className="input mt-1"
            placeholder="Additional information about your leave request..."
          />
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => reset()}
            className="btn btn-secondary"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary"
          >
            {isSubmitting ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Submitting...
              </>
            ) : (
              'Submit Request'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ApplyLeave