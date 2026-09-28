/**
 * Intelligent Resume Screening System - Frontend Application Logic
 */

let currentScreeningResults = [];
let demoResumes = [];
let scoreChartInstance = null;
let radarChartInstance = null;

// Initialize Dark Mode based on system preference
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark');
}

function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('bg-indigo-600', 'text-white', 'shadow');
        el.classList.add('text-slate-600', 'dark:text-slate-400');
    });

    document.getElementById(tabId).classList.remove('hidden');
    const btn = document.getElementById(`tabBtn_${tabId}`);
    if (btn) {
        btn.classList.add('bg-indigo-600', 'text-white', 'shadow');
        btn.classList.remove('text-slate-600', 'dark:text-slate-400');
    }

    if (tabId === 'analyticsTab') {
        renderCharts();
    }
}

function updateFileLabel(input) {
    const label = document.getElementById('fileLabelText');
    if (input.files && input.files.length > 0) {
        label.innerText = `${input.files.length} file(s) selected: ` + Array.from(input.files).map(f => f.name).join(', ');
    } else {
        label.innerText = 'Click or drag & drop resume files here';
    }
}

// Load Demo Dataset from API
async function loadSampleData() {
    try {
        const res = await fetch('/api/sample-data');
        const data = await res.json();

        if (data.sample_job_descriptions && data.sample_job_descriptions.length > 0) {
            const jd = data.sample_job_descriptions[0]; // Senior AI/ML Engineer
            document.getElementById('jobTitleInput').value = jd.title;
            document.getElementById('jdTextInput').value = jd.description;
            document.getElementById('reqSkillsInput').value = jd.required_skills.join(', ');
            document.getElementById('reqExpInput').value = jd.required_experience;
        }

        if (data.sample_resumes && data.sample_resumes.length > 0) {
            demoResumes = data.sample_resumes;
            document.getElementById('sampleTextFallbackSection').classList.remove('hidden');
            const badgesDiv = document.getElementById('demoLoadedBadges');
            badgesDiv.innerHTML = demoResumes.map(r => 
                `<span class="px-2 py-1 text-xs rounded-md bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-medium">📄 ${r.title}</span>`
            ).join(' ');
        }

        alert('Demo Job Description and 3 Sample Resumes successfully loaded into the form! Click "Run AI Resume Screening" to analyze.');
    } catch (err) {
        console.error('Failed to load sample data:', err);
    }
}

// Handle Batch Screening Submission
async function handleScreeningSubmit(event) {
    event.preventDefault();
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> <span>Analyzing with NLP & Scikit-Learn...</span>`;

    try {
        const jobTitle = document.getElementById('jobTitleInput').value;
        const jdText = document.getElementById('jdTextInput').value;
        const reqSkills = document.getElementById('reqSkillsInput').value;
        const reqExp = parseFloat(document.getElementById('reqExpInput').value) || 0.0;
        const fileInput = document.getElementById('resumeFilesInput');

        let rankedCandidates = [];

        if (fileInput.files && fileInput.files.length > 0) {
            // Upload actual files
            const formData = new FormData();
            formData.append('job_title', jobTitle);
            formData.append('job_description', jdText);
            formData.append('required_skills', reqSkills);
            formData.append('required_experience', reqExp);
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append('resumes', fileInput.files[i]);
            }

            const res = await fetch('/api/screen-bulk', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            rankedCandidates = data.ranked_candidates;
        } else if (demoResumes.length > 0) {
            // Screen demo resumes via single API calls
            const parsedSkills = reqSkills.split(',').map(s => s.trim()).filter(Boolean);
            const evals = [];

            for (let idx = 0; idx < demoResumes.length; idx++) {
                const res = await fetch('/api/screen-single', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        resume_text: demoResumes[idx].content,
                        job_description: {
                            title: jobTitle,
                            description: jdText,
                            required_skills: parsedSkills,
                            required_experience: reqExp
                        }
                    })
                });
                const item = await res.json();
                evals.push(item);
            }

            // Sort descending
            evals.sort((a, b) => b.composite_score - a.composite_score);
            evals.forEach((item, index) => item.rank = index + 1);
            rankedCandidates = evals;
        } else {
            alert('Please select resume files or click "Load Demo Dataset" first.');
            return;
        }

        currentScreeningResults = rankedCandidates;
        renderCandidateList(rankedCandidates);
        updateTopStats(rankedCandidates);
        document.getElementById('exportCsvBtn').classList.remove('hidden');

    } catch (err) {
        console.error('Error during screening:', err);
        alert('An error occurred during resume screening: ' + err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Run AI Resume Screening</span>`;
    }
}

function updateTopStats(candidates) {
    if (!candidates || candidates.length === 0) return;
    document.getElementById('statTotal').innerText = candidates.length;
    document.getElementById('statTopScore').innerText = candidates[0].composite_score + '%';

    const avgSkill = candidates.reduce((acc, c) => acc + c.score_breakdown.skill_match_percentage, 0) / candidates.length;
    document.getElementById('statAvgSkill').innerText = Math.round(avgSkill) + '%';

    const strongFits = candidates.filter(c => c.fit_category === 'Strong Match').length;
    document.getElementById('statStrongCount').innerText = strongFits;
}

function renderCandidateList(candidates) {
    const container = document.getElementById('candidateListContainer');
    const emptyState = document.getElementById('emptyRankState');

    if (!candidates || candidates.length === 0) {
        emptyState.classList.remove('hidden');
        container.innerHTML = '';
        return;
    }

    emptyState.classList.add('hidden');
    container.innerHTML = candidates.map(cand => {
        const badgeBg = cand.badge_color === 'green' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' :
                        cand.badge_color === 'blue' ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300' :
                        cand.badge_color === 'yellow' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
                        'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300';

        const rankBadge = cand.rank === 1 ? 'bg-amber-500 text-white' :
                          cand.rank === 2 ? 'bg-slate-400 text-white' :
                          cand.rank === 3 ? 'bg-amber-700 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300';

        return `
        <div class="glass-card rounded-xl p-4 transition hover:border-indigo-400 dark:hover:border-indigo-500 space-y-3">
            <div class="flex items-start justify-between">
                <div class="flex items-center space-x-3">
                    <span class="w-7 h-7 rounded-lg font-bold text-xs flex items-center justify-center ${rankBadge}">
                        #${cand.rank}
                    </span>
                    <div>
                        <h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center space-x-2">
                            <span>${cand.candidate_name}</span>
                            <span class="text-[11px] px-2 py-0.5 rounded-full font-semibold ${badgeBg}">
                                ${cand.fit_category}
                            </span>
                        </h4>
                        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            <i class="fa-regular fa-envelope mr-1"></i>${cand.email || 'No email provided'} | 
                            <i class="fa-solid fa-briefcase ml-1 mr-1"></i>${cand.candidate_info.experience_years} Yrs Exp
                        </p>
                    </div>
                </div>

                <div class="text-right">
                    <div class="text-xl font-extrabold text-indigo-600 dark:text-indigo-400">
                        ${cand.composite_score}%
                    </div>
                    <span class="text-[10px] text-slate-400 font-medium">Match Score</span>
                </div>
            </div>

            <!-- Score Progress Bars -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                <div>
                    <span class="text-[11px] text-slate-500">TF-IDF Vector</span>
                    <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-1 overflow-hidden">
                        <div class="bg-indigo-500 h-1.5 rounded-full" style="width: ${cand.score_breakdown.tfidf_similarity}%"></div>
                    </div>
                </div>
                <div>
                    <span class="text-[11px] text-slate-500">Skill Overlap</span>
                    <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-1 overflow-hidden">
                        <div class="bg-emerald-500 h-1.5 rounded-full" style="width: ${cand.score_breakdown.skill_match_percentage}%"></div>
                    </div>
                </div>
                <div>
                    <span class="text-[11px] text-slate-500">Experience</span>
                    <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-1 overflow-hidden">
                        <div class="bg-purple-500 h-1.5 rounded-full" style="width: ${cand.score_breakdown.experience_score}%"></div>
                    </div>
                </div>
                <div>
                    <span class="text-[11px] text-slate-500">Education</span>
                    <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-1 overflow-hidden">
                        <div class="bg-amber-500 h-1.5 rounded-full" style="width: ${cand.score_breakdown.education_score}%"></div>
                    </div>
                </div>
            </div>

            <div class="flex justify-end pt-1">
                <button onclick="openModal(${cand.rank - 1})" class="text-xs text-indigo-600 dark:text-indigo-400 font-semibold hover:underline flex items-center space-x-1">
                    <span>View AI Breakdown & Skills Gap</span>
                    <i class="fa-solid fa-chevron-right text-[10px]"></i>
                </button>
            </div>
        </div>
        `;
    }).join('');
}

function openModal(index) {
    const cand = currentScreeningResults[index];
    if (!cand) return;

    const modalContent = document.getElementById('modalContent');
    const matchedSkillsPills = cand.skill_gap_analysis.matched_skills.map(s => 
        `<span class="px-2 py-0.5 text-xs rounded-md bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-medium">✓ ${s}</span>`
    ).join(' ') || '<span class="text-xs text-slate-400">None matched</span>';

    const missingSkillsPills = cand.skill_gap_analysis.missing_skills.map(s => 
        `<span class="px-2 py-0.5 text-xs rounded-md bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 font-medium">✗ ${s}</span>`
    ).join(' ') || '<span class="text-xs text-slate-400">None missing</span>';

    const insightsList = cand.ai_insights.map(i => 
        `<li class="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-1.5"><i class="fa-solid fa-angle-right text-indigo-500 mt-0.5"></i><span>${i}</span></li>`
    ).join('');

    modalContent.innerHTML = `
        <div class="space-y-4">
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">${cand.candidate_name}</h3>
                    <p class="text-xs text-slate-500">${cand.email} | ${cand.phone || 'N/A'}</p>
                </div>
                <span class="text-2xl font-black text-indigo-600 dark:text-indigo-400">${cand.composite_score}%</span>
            </div>

            <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl space-y-2 border border-slate-200 dark:border-slate-800">
                <h4 class="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">AI Assessment Summary</h4>
                <ul class="space-y-1">${insightsList}</ul>
            </div>

            <div>
                <h4 class="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">Matched Skills (${cand.skill_gap_analysis.matched_skills.length})</h4>
                <div class="flex flex-wrap gap-1.5">${matchedSkillsPills}</div>
            </div>

            <div>
                <h4 class="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">Missing Required Skills (${cand.skill_gap_analysis.missing_skills.length})</h4>
                <div class="flex flex-wrap gap-1.5">${missingSkillsPills}</div>
            </div>
        </div>
    `;

    document.getElementById('detailModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('detailModal').classList.add('hidden');
}

async function exportCsvReport() {
    if (!currentScreeningResults || currentScreeningResults.length === 0) return;

    try {
        const res = await fetch('/api/export-csv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentScreeningResults)
        });

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resume_screening_report_${Date.now()}.csv`;
        a.click();
    } catch (err) {
        console.error('Export CSV failed:', err);
    }
}

async function parseSingleResume() {
    const fileInput = document.getElementById('singleResumeInput');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select a resume file first.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const res = await fetch('/api/parse-resume', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        const card = document.getElementById('parsedResultCard');
        card.classList.remove('hidden');
        card.innerHTML = `
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <span class="text-xs font-bold text-slate-400">Candidate Name</span>
                    <p class="font-semibold text-sm text-slate-800 dark:text-slate-200">${data.candidate_name}</p>
                </div>
                <div>
                    <span class="text-xs font-bold text-slate-400">Estimated Experience</span>
                    <p class="font-semibold text-sm text-slate-800 dark:text-slate-200">${data.experience_years} Years</p>
                </div>
                <div>
                    <span class="text-xs font-bold text-slate-400">Email</span>
                    <p class="font-semibold text-sm text-slate-800 dark:text-slate-200">${data.email || 'N/A'}</p>
                </div>
                <div>
                    <span class="text-xs font-bold text-slate-400">Degrees</span>
                    <p class="font-semibold text-sm text-slate-800 dark:text-slate-200">${data.education.join(', ') || 'N/A'}</p>
                </div>
            </div>
            <div>
                <span class="text-xs font-bold text-slate-400">Extracted Skills (${data.skills.flat_list.length})</span>
                <div class="flex flex-wrap gap-1 mt-1.5">
                    ${data.skills.flat_list.map(s => `<span class="px-2 py-0.5 text-xs rounded bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-medium">${s}</span>`).join(' ')}
                </div>
            </div>
        `;
    } catch (err) {
        alert('Failed to parse resume: ' + err.message);
    }
}

function renderCharts() {
    if (!currentScreeningResults || currentScreeningResults.length === 0) return;

    const names = currentScreeningResults.map(c => c.candidate_name);
    const scores = currentScreeningResults.map(c => c.composite_score);

    // Score Bar Chart
    const ctxBar = document.getElementById('scoreChart').getContext('2d');
    if (scoreChartInstance) scoreChartInstance.destroy();
    scoreChartInstance = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [{
                label: 'Match Score (%)',
                data: scores,
                backgroundColor: 'rgba(99, 102, 241, 0.7)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // Radar Chart for Top Candidate
    const topCand = currentScreeningResults[0];
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    if (radarChartInstance) radarChartInstance.destroy();
    radarChartInstance = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: ['TF-IDF Match', 'Skill Overlap', 'Experience Score', 'Education Level'],
            datasets: [{
                label: topCand.candidate_name,
                data: [
                    topCand.score_breakdown.tfidf_similarity,
                    topCand.score_breakdown.skill_match_percentage,
                    topCand.score_breakdown.experience_score,
                    topCand.score_breakdown.education_score
                ],
                fill: true,
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderColor: 'rgb(16, 185, 129)',
                pointBackgroundColor: 'rgb(16, 185, 129)'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}
