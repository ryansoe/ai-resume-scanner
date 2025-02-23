// src/pages/CreateJob.jsx
import { useState } from 'react'

export default function CreateJob() {
  const [formData, setFormData] = useState({ title: '', description: '' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')
    setError('')
    const token = localStorage.getItem('token')
    if (!token) {
      setError('You must be logged in.')
      return
    }

    try {
      const res = await fetch('https://fastapi-resume-4suu.onrender.com/jobs/create-job', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to create job')
      }
      setMessage(data.message)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-md mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Create Job</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}
      {message && <p className="bg-green-100 text-green-700 p-2 mb-2">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">Job Title</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="w-full border p-2"
            required
          />
        </div>
        <div>
          <label className="block mb-1">Job Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="w-full border p-2"
            rows="5"
            required
          />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2">
          Create
        </button>
      </form>
    </div>
  )
}