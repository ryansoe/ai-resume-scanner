// src/Router.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import UploadResume from './pages/UploadResume.jsx'
import MyResumes from './pages/MyResumes.jsx'
import CreateJob from './pages/CreateJob.jsx'
import JobList from './pages/JobList.jsx'
import Navbar from './components/Navbar.jsx'
import JobMatching from './pages/JobMatching.jsx'

export default function AppRouter() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/resumes/upload" element={<UploadResume />} />
        <Route path="/resumes" element={<MyResumes />} />
        <Route path="/jobs/create" element={<CreateJob />} />
        <Route path="/jobs" element={<JobList />} />
        <Route path="/job-matching" element={<JobMatching />} />
      </Routes>
    </Router>
  )
}