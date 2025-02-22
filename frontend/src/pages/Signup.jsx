// src/pages/Signup.jsx
import { useState } from 'react'

export default function Signup() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: ''
  })
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      const res = await fetch('http://127.0.0.1:8000/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to register')
      }
      const data = await res.json()
      setMessage(data.message)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-md mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Sign Up</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}
      {message && <p className="bg-green-100 text-green-700 p-2 mb-2">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="w-full border p-2"
            required
          />
        </div>
        <div>
          <label className="block mb-1">Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>
        <div>
          <label className="block mb-1">Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full border p-2"
            required
          />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2">
          Register
        </button>
      </form>
    </div>
  )
}