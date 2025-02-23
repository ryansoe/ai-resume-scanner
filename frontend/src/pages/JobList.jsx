// src/pages/JobList.jsx
import { useEffect, useState } from 'react'

export default function JobList() {
  const [jobs, setJobs] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setError('Please login first.')
      return
    }

    // Assume you have GET /jobs or similar to list all jobs
    fetch('https://fastapi-resume-4suu.onrender.com/jobs/list', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (data.jobs) {
          setJobs(data.jobs)
        } else {
          setError('Failed to fetch jobs')
        }
      })
      .catch(err => setError(err.message))
  }, [])

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Job Listings</h2>
      {error && <p className="bg-red-100 text-red-700 p-2 mb-2">{error}</p>}
      <ul>
        {jobs.map(job => (
          <li key={job._id} className="mb-2 border-b pb-2">
            <p className="font-semibold">{job.title}</p>
            <p>{job.description}</p>
            {/* Could add a "Match Resumes" button that calls POST /jobs/match/{job._id} */}
          </li>
        ))}
      </ul>
    </div>
  )
}