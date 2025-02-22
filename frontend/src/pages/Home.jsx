// src/pages/Home.jsx
export default function Home() {
    return (
      <div className="max-w-3xl mx-auto p-4">
        <h2 className="text-2xl font-bold mb-4">Welcome to the Resume Scanner!</h2>
  
        <p className="mb-4">
          This website helps you upload your resumes, automatically extract skills, and match them
          against job descriptions to see which resume is best suited for each job.
        </p>
  
        <ol className="list-decimal list-inside space-y-2">
          <li>
            <strong>Sign Up or Log In:</strong> Click on the “Sign Up” or “Login” link in the 
            navigation bar. Once you’ve created an account (or logged in), you’ll have access 
            to all features.
          </li>
          <li>
            <strong>Upload Resumes:</strong> Go to “Upload Resume” and select one or more PDF 
            files. The system will store your resume text and extract key skills automatically.
          </li>
          <li>
            <strong>View Uploaded Resumes:</strong> Check “My Resumes” to see all your uploaded 
            resumes, along with the skills the AI extracted.
          </li>
          <li>
            <strong>Create a Job & Match Resumes:</strong> Navigate to “Job Matching” to create 
            a new job listing by providing a title and description. The system will extract 
            required skills, then rank your uploaded resumes based on skill overlap.
          </li>
          <li>
            <strong>Analyze Results:</strong> The “Job Matching” page shows each resume’s 
            relevance score and matched skills, so you know which resume is best tailored 
            for the job.
          </li>
        </ol>
  
        <p className="mt-4">
          If you have any issues or questions, please reach out to ryansoe26@gmail.com. 
          We hope this Resume Scanner makes your job hunting/recruiting more efficient and effective!
        </p>
      </div>
    )
  }