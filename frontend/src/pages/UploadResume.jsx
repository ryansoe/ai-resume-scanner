// src/pages/UploadResume.jsx
import { useState } from 'react'

export default function UploadResume() {
  const [selectedFiles, setSelectedFiles] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    setSelectedFiles(e.target.files)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')
    setError('')
    if (!selectedFiles) return

    const token = localStorage.getItem('token')
    if (!token) {
      setError('You must be logged in.')
      return
    }

    try {
      const formData = new FormData()
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i])
      }

      const res = await fetch('http://127.0.0.1:8000/resumes/upload-multiple', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed')
      }
      setMessage(data.message)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-md mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Upload Resume(s)</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}
      {message && <p className="bg-green-100 text-green-700 p-2 mb-2">{message}</p>}

      <form onSubmit={handleSubmit}>
        <input
          type="file"
          multiple
          accept="application/pdf"
          onChange={handleFileChange}
          className="mb-4"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2">
          Upload
        </button>
      </form>
    </div>
  )
}