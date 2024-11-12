'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function StudentDashboard() {
  const [studentData, setStudentData] = useState(null)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/student-dashboard')
        const data = await response.json()

        if (response.ok) {
          setStudentData(data.student_data)
        } else {
          setError(data.message)
          if (response.status === 401) {
            router.push('/')
          }
        }
      } catch (err) {
        setError('An error occurred. Please try again.')
      }
    }

    fetchData()
  }, [router])

  const handleTARequest = async (e: React.FormEvent) => {
    e.preventDefault()
    // Implement the TA request logic here
  }

  if (error) {
    return <div className="text-red-500">{error}</div>
  }

  if (!studentData) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Student Dashboard</h2>
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Student Information</h3>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">SRN</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{studentData.SRN}</dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{studentData.Name}</dd>
            </div>
            {/* Add more student details as needed */}
          </dl>
        </div>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Apply for TA Position</h3>
          <div className="mt-2 max-w-xl text-sm text-gray-500">
            <p>Submit a request to become a Teaching Assistant for a specific course.</p>
          </div>
          <form onSubmit={handleTARequest} className="mt-5 sm:flex sm:items-center">
            <div className="w-full sm:max-w-xs">
              <label htmlFor="course" className="sr-only">Course</label>
              <select
                id="course"
                name="course"
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                defaultValue=""
              >
                <option value="" disabled>Select a course</option>
                {/* Add course options here */}
                <option value="course1">Course 1</option>
                <option value="course2">Course 2</option>
              </select>
            </div>
            <button
              type="submit"
              className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Apply
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}