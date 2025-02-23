// src/pages/MyResumes.jsx
import { useEffect, useState } from 'react'

export default function MyResumes() {
  const [resumes, setResumes] = useState([])
  const [error, setError] = useState('')

  const token = localStorage.getItem('token')

  useEffect(() => {
    if (!token) {
      setError('Please login first.')
      return
    }

    fetch('https://fastapi-resume-4suu.onrender.com/resumes/my-resumes', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (data.resumes) {
          setResumes(data.resumes)
        } else {
          setError('Failed to load resumes')
        }
      })
      .catch(err => setError(err.message))
  }, [token])

  const handleDelete = async (resumeId) => {
    if (!token) return
    try {
      const res = await fetch(`https://fastapi-resume-4suu.onrender.com/resumes/delete/${resumeId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to delete')
      }
      // Remove from local state
      setResumes(resumes.filter(r => r._id !== resumeId))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">My Resumes</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}
      
      <ul>
        {resumes.map((resume) => (
          <li key={resume._id} className="mb-2 border-b pb-2 flex justify-between items-center">
            <div>
              <p className="font-semibold">{resume.filename}</p>
              {resume.skills && <p className="text-gray-600 text-sm">Skills: {resume.skills.join(', ')}</p>}
            </div>
            <button
              onClick={() => handleDelete(resume._id)}
              className="text-red-600 hover:text-red-800"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}