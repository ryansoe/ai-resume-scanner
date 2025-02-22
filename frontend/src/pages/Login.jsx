// src/pages/Login.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await fetch('http://127.0.0.1:8000/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: formData.username,
          password: formData.password
        })
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to login')
      }
      const data = await res.json()
      // store token
      localStorage.setItem('token', data.access_token)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-md mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Login</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}

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
          Login
        </button>
      </form>
    </div>
  )
}