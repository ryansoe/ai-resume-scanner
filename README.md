# 🏆 AI Resume Scanner 🏆

*An end-to-end web application for uploading resumes, automatically extracting skills, and matching them against job descriptions.*

https://ai-resume-scanner-frontend.onrender.com/job-matching

## 📌 Overview
AI Resume Screener is a **React + FastAPI** application that streamlines the process of **resume management** and **job matching**. Users can **upload multiple PDF resumes**, have their **skills extracted automatically**, and compare them against **job descriptions** to see which resume is best suited.  
 
The site is currently **live**, allowing users to **create accounts**, **upload resumes**, **match** to jobs, and **delete** unwanted resumes – all in a clean, easy-to-use interface.

## ✨ Features
✅ **User Authentication** – Sign up, log in, and log out to secure your personal data.  
✅ **Automatic Skill Extraction** – Resumes are parsed using OpenAI, with extracted skills stored in MongoDB.  
✅ **Multi-file Resume Upload** – Users can upload several PDF resumes at once.  
✅ **Job Creation & Matching** – Create a job description, extract required skills, and rank your resumes based on overlap.  
✅ **Resume Deletion** – Remove any outdated or incorrect resumes from your profile.  
✅ **Intuitive UI** – A React frontend with Tailwind CSS for clean styling and easy navigation.  
✅ **Toast Notifications** – Get immediate feedback on login, logout, errors, and more.  

## 🚀 Technologies Used
- **Python FastAPI** – Backend web framework  
- **React** – Frontend library for building user interfaces  
- **Tailwind CSS** – Utility-first CSS framework for rapid UI development  
- **MongoDB** – NoSQL database for storing resumes, users, and jobs  
- **OpenAI API** – Powers skill extraction and job description parsing  
- **PyPDF2** – PDF parsing for resume text extraction  
- **JWT** – Secure user authentication  
- **React Toastify** – Toast notifications for user feedback  

*(In the future, we plan to integrate **PyTorch** for advanced matching and ML features.)*

## 📖 How It Works

1. **Sign Up / Log In**  
   - Users create accounts or sign in.  
   - A JWT token is stored for secure requests.

2. **Upload Resumes**  
   - Users upload PDF resumes (multi-file supported).  
   - The app extracts text and immediately calls OpenAI to parse out skills, which are then stored in MongoDB.

3. **Create a Job**  
   - Provide a job title and description.  
   - The system extracts required skills (OpenAI) and stores them.

4. **Match Resumes**  
   - The site ranks all of your uploaded resumes based on **skill overlap** with the job.  
   - Displays a **score** and matched skills for each resume.

5. **Manage Resumes**  
   - A “My Resumes” page to view and delete any uploaded resumes.

6. **Toast Notifications**  
   - On login, logout, and key actions, to give immediate user feedback.

## 🏗 Future Improvements
- **PyTorch Model for Enhanced Matching**  
  - Integrate a skill categorization or semantic matching model to improve job ranking accuracy.  
- **Job Tracking System**  
  - Let users track applications, set statuses (Applied, Interviewing, Offered), and record notes.  
- **Resume Feedback**  
  - Provide personalized suggestions on how to optimize resumes for specific job postings.  
- **Caching and Optimization**  
  - Reduce repeated OpenAI calls by caching embeddings or skill sets.


## 👨‍💻 Author
**Ryan Soe**

- **GitHub**: [github/ryansoe](https://github.com/ryansoe)  
- **LinkedIn**: [linkedin/ryansoe](https://linkedin.com/in/ryan-soe-2596b6309/)

Feel free to open **issues** or **pull requests** if you have suggestions or find any bugs.  
Enjoy using the **AI Resume Scanner**!
