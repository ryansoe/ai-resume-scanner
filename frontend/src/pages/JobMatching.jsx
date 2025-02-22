// src/pages/JobMatching.jsx
import { useState } from 'react'

export default function JobMatching() {
  const [jobData, setJobData] = useState({
    title: '',
    description: ''
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [rankedResumes, setRankedResumes] = useState([])
  const [jobId, setJobId] = useState(null)

  const handleChange = (e) => {
    setJobData({
      ...jobData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')
    setError('')
    setRankedResumes([])

    const token = localStorage.getItem('token')
    if (!token) {
      setError('You must be logged in.')
      return
    }

    try {
      // 1. Create Job
      const createRes = await fetch('http://127.0.0.1:8000/jobs/create-job', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(jobData)
      })
      const createData = await createRes.json()
      if (!createRes.ok) {
        throw new Error(createData.detail || 'Failed to create job')
      }

      setMessage(createData.message) // e.g. "Job created and skills extracted successfully"
      setJobId(createData.job_id)    // Save the newly created job_id

      // 2. Match Resumes
      const matchRes = await fetch(`http://127.0.0.1:8000/jobs/match/${createData.job_id}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      const matchData = await matchRes.json()
      if (!matchRes.ok) {
        throw new Error(matchData.detail || 'Failed to match resumes')
      }

      // Display the matched resumes
      setRankedResumes(matchData.matches) // e.g. an array of resumes with scores

    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Create Job & Match Resumes</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}
      {message && <p className="bg-green-100 text-green-700 p-2 mb-2">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label className="block mb-1 font-semibold">Job Title</label>
          <input
            type="text"
            name="title"
            value={jobData.title}
            onChange={handleChange}
            className="w-full border p-2"
            required
          />
        </div>
        <div>
          <label className="block mb-1 font-semibold">Job Description</label>
          <textarea
            name="description"
            value={jobData.description}
            onChange={handleChange}
            className="w-full border p-2"
            rows="5"
            required
          />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2">
          Create Job & View Rankings
        </button>
      </form>

      {/* Display matched resumes */}
      {rankedResumes.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-2">Resume Rankings</h3>
          <table className="w-full border">
            <thead className="bg-gray-100">
              <tr>
                {/* Removed Resume ID column */}
                <th className="p-2 border">Filename</th>
                <th className="p-2 border">Score</th>
                <th className="p-2 border">Matched Skills</th>
              </tr>
            </thead>
            <tbody>
              {rankedResumes.map((resume) => (
                /* Use resume_id as the key, but don't display it */
                <tr key={resume.resume_id}>
                  <td className="p-2 border">{resume.filename}</td>
                  <td className="p-2 border text-center">
                    {resume.overlap_score.toFixed(2)}
                  </td>
                  <td className="p-2 border">
                    {resume.matched_skills && resume.matched_skills.join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}