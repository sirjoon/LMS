import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken')
      localStorage.removeItem('userRole')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action')
      return Promise.reject(error)
    }

    if (error.response?.status === 422) {
      // Validation error - show specific message
      const detail = error.response.data?.detail
      if (typeof detail === 'string') {
        toast.error(detail)
      } else if (Array.isArray(detail)) {
        detail.forEach((err: any) => toast.error(err.msg))
      }
      return Promise.reject(error)
    }

    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
      return Promise.reject(error)
    }

    // Default error handling
    const message = error.response?.data?.detail || error.message || 'Something went wrong'
    toast.error(message)
    
    return Promise.reject(error)
  }
)

export default api