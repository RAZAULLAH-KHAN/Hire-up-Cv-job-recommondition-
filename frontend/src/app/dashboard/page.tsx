"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { Upload, Search, Check, X, Loader2, Sparkles, FileText, ChevronRight } from "lucide-react";

export default function Dashboard() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizedCv, setOptimizedCv] = useState<string | null>(null);

  useEffect(() => {
    if (!Cookies.get("token")) {
      router.push("/");
    }
  }, [router]);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = Cookies.get("token");
      await fetch("http://localhost:8000/api/v1/upload-cv", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      fetchMatches();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const token = Cookies.get("token");
      const res = await fetch("http://localhost:8000/api/v1/get-matches", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setJobs(data.matches);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (jobId: string, action: "save" | "discard") => {
    if (action === "save") {
      const token = Cookies.get("token");
      await fetch(`http://localhost:8000/api/v1/save-job/${jobId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    setJobs((prev) => prev.filter((j) => j.id !== jobId));
    setSelectedJob(null);
  };

  const handleOptimize = async (jobDescription: string) => {
    setOptimizing(true);
    try {
      const token = Cookies.get("token");
      const res = await fetch("http://localhost:8000/api/v1/optimize-cv", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ job_description: jobDescription })
      });
      const data = await res.json();
      setOptimizedCv(data.optimized_experience);
    } catch (err) {
      console.error(err);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-8 flex flex-col items-center">
      <div className="w-full max-w-5xl space-y-8">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-card/30 p-6 rounded-2xl border border-border backdrop-blur-md">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Your Dashboard</h1>
            <p className="text-muted-foreground mt-1">Upload your CV to see AI-powered job matches.</p>
          </div>
          <button 
            onClick={() => { Cookies.remove("token"); router.push("/"); }}
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Sign Out
          </button>
        </div>

        {/* Upload Section */}
        <div className="bg-card p-6 rounded-2xl border border-border flex flex-col sm:flex-row items-center gap-4 shadow-sm">
          <div className="flex-1 w-full relative">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="w-full px-4 py-3 border-2 border-dashed border-primary/50 rounded-xl flex items-center justify-center gap-3 bg-primary/5 text-primary hover:bg-primary/10 transition-colors">
              <Upload className="w-5 h-5" />
              <span className="font-medium">{file ? file.name : "Choose PDF Resume..."}</span>
            </div>
          </div>
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            Analyze & Match
          </button>
          <button
            onClick={fetchMatches}
            className="px-6 py-3 bg-secondary text-secondary-foreground rounded-xl font-medium hover:bg-secondary/80 transition-all"
          >
            Refresh Matches
          </button>
        </div>

        {/* Main Content */}
        <div className="grid md:grid-cols-2 gap-8">
          
          {/* Job List */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-primary" /> Recommended Roles
            </h2>
            {jobs.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground border border-border rounded-2xl bg-card/30">
                No matches found. Upload a CV to begin.
              </div>
            ) : (
              <div className="space-y-3">
                {jobs.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedJob?.id === job.id 
                        ? 'border-primary bg-primary/5 shadow-md' 
                        : 'border-border bg-card hover:border-primary/50 hover:bg-card/80'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-lg">{job.title}</h3>
                        <p className="text-muted-foreground text-sm">{job.company} • {job.location}</p>
                      </div>
                      <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold">
                        {(job.score * 100).toFixed(0)}% Match
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Job Details */}
          <div className="sticky top-8 space-y-4">
             {selectedJob ? (
               <div className="bg-card border border-border rounded-2xl p-6 shadow-xl relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-4 flex gap-2">
                    <button onClick={() => handleAction(selectedJob.id, "discard")} className="p-2 bg-destructive/10 text-destructive rounded-full hover:bg-destructive hover:text-white transition-colors">
                      <X className="w-5 h-5" />
                    </button>
                    <button onClick={() => handleAction(selectedJob.id, "save")} className="p-2 bg-green-500/10 text-green-500 rounded-full hover:bg-green-500 hover:text-white transition-colors">
                      <Check className="w-5 h-5" />
                    </button>
                 </div>
                 
                 <h2 className="text-2xl font-bold pr-20">{selectedJob.title}</h2>
                 <p className="text-muted-foreground text-lg mb-6">{selectedJob.company}</p>

                 <div className="space-y-6">
                   <div>
                     <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-500" /> Matched Skills
                     </h4>
                     <div className="flex flex-wrap gap-2">
                       {selectedJob.matched_skills.map((s: string, i: number) => (
                         <span key={i} className="px-2.5 py-1 bg-green-500/10 text-green-500 border border-green-500/20 rounded-md text-sm font-medium">
                           {s}
                         </span>
                       ))}
                       {selectedJob.matched_skills.length === 0 && <span className="text-sm text-muted-foreground">None</span>}
                     </div>
                   </div>

                   <div>
                     <h4 className="font-medium mb-3 flex items-center gap-2">
                        <X className="w-4 h-4 text-destructive" /> Missing Skills
                     </h4>
                     <div className="flex flex-wrap gap-2">
                       {selectedJob.missing_skills.map((s: string, i: number) => (
                         <span key={i} className="px-2.5 py-1 bg-destructive/10 text-destructive border border-destructive/20 rounded-md text-sm font-medium">
                           {s}
                         </span>
                       ))}
                       {selectedJob.missing_skills.length === 0 && <span className="text-sm text-muted-foreground">None</span>}
                     </div>
                   </div>

                   <div className="pt-4 border-t border-border mt-6">
                     <button
                       onClick={() => handleOptimize("Job requires: " + selectedJob.title)} // Simplified for mock
                       disabled={optimizing}
                       className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
                     >
                       {optimizing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                       Tailor CV for this Job
                     </button>
                     
                     {optimizedCv && (
                       <div className="mt-4 p-4 bg-primary/5 border border-primary/20 rounded-xl">
                         <h4 className="text-sm font-semibold text-primary mb-2 flex items-center gap-2">
                            <FileText className="w-4 h-4" /> Optimized Experience Bullet Points
                         </h4>
                         <p className="text-sm text-foreground/80 whitespace-pre-wrap">{optimizedCv}</p>
                       </div>
                     )}
                   </div>
                 </div>
               </div>
             ) : (
               <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-center p-8 border border-border border-dashed rounded-2xl bg-card/30">
                 <div className="p-4 bg-primary/10 rounded-full mb-4">
                   <ChevronRight className="w-8 h-8 text-primary" />
                 </div>
                 <h3 className="text-xl font-medium text-foreground">Select a job</h3>
                 <p className="text-muted-foreground mt-2">Click on any role from the left to view ATS Gap Analysis and AI tailoring options.</p>
               </div>
             )}
          </div>
        </div>
        
      </div>
    </div>
  );
}
