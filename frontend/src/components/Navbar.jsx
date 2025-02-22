// src/components/Navbar.jsx
import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
    const navigate = useNavigate()

    const handleSignOut = () => {
      localStorage.removeItem('token') // remove JWT
      navigate('/login')              // redirect to login
    }   

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-2 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">
          AI Resume Screener
        </Link>
        <div className="space-x-4">
          <Link to="/login" className="text-gray-700 hover:text-blue-600">
            Login
          </Link>
          <Link to="/signup" className="text-gray-700 hover:text-blue-600">
            Sign Up
          </Link>
          <Link to="/job-matching" className="text-gray-700 hover:text-blue-600">
              Job Matching
            </Link>
          <Link to="/resumes/upload" className="text-gray-700 hover:text-blue-600">
            Upload Resume
          </Link>
          <Link to="/resumes" className="text-gray-700 hover:text-blue-600">
            My Resumes
          </Link>
          <button onClick={handleSignOut} className="text-red-600">
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  )
}