/**
 * SchemeScout - Frontend Application
 * Punjab Government Welfare Schemes Finder
 * Built by Bit-Wise 4
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let currentStep = 1;
const totalSteps = 4;
let userData = {};
let matchedSchemes = [];
let userDocuments = [];

// Document List (Common documents for Punjab schemes)
const commonDocuments = [
    { id: 'aadhar', name: 'Aadhar Card', icon: 'id-card' },
    { id: 'income_cert', name: 'Income Certificate', icon: 'file-text', expiry: true },
    { id: 'caste_cert', name: 'Caste/Category Certificate', icon: 'file-badge' },
    { id: 'residence', name: 'Residence Proof', icon: 'home' },
    { id: 'bank_passbook', name: 'Bank Passbook', icon: 'landmark' },
    { id: 'photo', name: 'Passport Photo', icon: 'camera' },
    { id: 'ration_card', name: 'Ration Card (BPL/APL)', icon: 'credit-card' },
    { id: 'birth_cert', name: 'Birth Certificate', icon: 'baby' },
    { id: 'education', name: 'Education Certificate', icon: 'graduation-cap' },
    { id: 'labour_card', name: 'Labour/BOCW Card', icon: 'hard-hat' },
    { id: 'disability_cert', name: 'Disability Certificate', icon: 'accessibility' },
    { id: 'land_record', name: 'Land Record/Fard', icon: 'map' }
];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Setup form handler
    const form = document.getElementById('schemeForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Initialize document tracker
    initializeDocumentTracker();
    
    // Load deadline alerts
    loadDeadlineAlerts();
    
    // Setup real-time validation
    setupValidation();
}

// Step Navigation
function changeStep(direction) {
    const newStep = currentStep + direction;
    
    // Validate current step before moving forward
    if (direction > 0 && !validateStep(currentStep)) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    if (newStep >= 1 && newStep <= totalSteps) {
        // Hide current step
        document.getElementById(`step${currentStep}`).classList.add('hidden');
        
        // Show new step
        document.getElementById(`step${newStep}`).classList.remove('hidden');
        
        currentStep = newStep;
        updateProgressBar();
        updateNavigationButtons();
        
        // If moving to review step, populate review
        if (currentStep === 4) {
            populateReview();
        }
        
        // Reinitialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function validateStep(step) {
    const stepElement = document.getElementById(`step${step}`);
    const inputs = stepElement.querySelectorAll('input[required], select[required]');
    
    let isValid = true;
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('border-red-500');
            isValid = false;
        } else {
            input.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

function updateProgressBar() {
    const progress = (currentStep / totalSteps) * 100;
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('currentStep').textContent = currentStep;
    
    const stepLabels = ['Personal Information', 'Category & Income', 'Occupation & Location', 'Review & Submit'];
    document.getElementById('stepLabel').textContent = stepLabels[currentStep - 1];
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    // Show/hide previous button
    if (currentStep > 1) {
        prevBtn.classList.remove('hidden');
        prevBtn.classList.add('flex');
    } else {
        prevBtn.classList.add('hidden');
        prevBtn.classList.remove('flex');
    }
    
    // Show/hide next and submit buttons
    if (currentStep === totalSteps) {
        nextBtn.classList.add('hidden');
        submitBtn.classList.remove('hidden');
        submitBtn.classList.add('flex');
    } else {
        nextBtn.classList.remove('hidden');
        submitBtn.classList.add('hidden');
        submitBtn.classList.remove('flex');
    }
}

function populateReview() {
    const form = document.getElementById('schemeForm');
    const formData = new FormData(form);
    
    userData = {
        name: formData.get('name'),
        age: parseInt(formData.get('age')),
        gender: formData.get('gender'),
        phone: formData.get('phone') || 'Not provided',
        category: formData.get('category'),
        annual_income: parseFloat(formData.get('annual_income')) || 0,
        occupation: formData.get('occupation'),
        region: formData.get('region')
    };
    
    const reviewHTML = `
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="p-4 bg-white rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Name</p>
                <p class="font-semibold text-gray-900">${userData.name}</p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Age</p>
                <p class="font-semibold text-gray-900">${userData.age} years</p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Gender</p>
                <p class="font-semibold text-gray-900">${userData.gender}</p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Category</p>
                <p class="font-semibold text-gray-900">${userData.category}</p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Annual Income</p>
                <p class="font-semibold text-gray-900">Rs. ${userData.annual_income.toLocaleString()}</p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Occupation</p>
                <p class="font-semibold text-gray-900">${userData.occupation}</p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200 sm:col-span-2">
                <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Region</p>
                <p class="font-semibold text-gray-900">${userData.region}, Punjab</p>
            </div>
        </div>
    `;
    
    document.getElementById('reviewContent').innerHTML = reviewHTML;
}

// Form Submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/check-eligibility`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to check eligibility');
        }
        
        const data = await response.json();
        matchedSchemes = data.all_results || [];
        
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        // Show error message and use mock data for demonstration
        showToast('Backend API unavailable. Showing demo data with real Punjab schemes.', 'warning');
        displayMockResults();
    } finally {
        showLoading(false);
    }
}

function displayResults(data) {
    // Hide form, show results
    document.getElementById('eligibility-form').classList.add('hidden');
    document.getElementById('hero').classList.add('hidden');
    document.getElementById('results').classList.remove('hidden');
    
    // Display summary
    const summaryHTML = `
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
                <h2 class="text-2xl font-bold text-gray-900">Results for ${data.user_profile.name}</h2>
                <p class="text-gray-600">Based on your profile, we found ${data.summary.total_schemes} schemes</p>
            </div>
            <button onclick="resetForm()" class="px-4 py-2 text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50 transition-colors flex items-center gap-2">
                <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                New Search
            </button>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="text-center p-4 bg-green-50 rounded-lg">
                <p class="text-3xl font-bold text-green-600">${data.summary.eligible_count}</p>
                <p class="text-sm text-green-700">Eligible</p>
            </div>
            <div class="text-center p-4 bg-amber-50 rounded-lg">
                <p class="text-3xl font-bold text-amber-600">${data.summary.potential_count}</p>
                <p class="text-sm text-amber-700">Potential</p>
            </div>
            <div class="text-center p-4 bg-blue-50 rounded-lg">
                <p class="text-3xl font-bold text-blue-600">${data.summary.partial_count}</p>
                <p class="text-sm text-blue-700">Partial Match</p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-lg">
                <p class="text-3xl font-bold text-gray-600">${data.summary.total_schemes}</p>
                <p class="text-sm text-gray-700">Total Schemes</p>
            </div>
        </div>
    `;
    
    document.getElementById('resultsSummary').innerHTML = summaryHTML;
    
    // Display scheme cards
    const cardsHTML = data.all_results.map(scheme => createSchemeCard(scheme)).join('');
    document.getElementById('schemeCards').innerHTML = cardsHTML;
    
    // Reinitialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function createSchemeCard(scheme) {
    const statusClass = scheme.status.toLowerCase().replace(' ', '-');
    const scoreClass = scheme.match_score >= 80 ? 'high' : scheme.match_score >= 50 ? 'medium' : scheme.match_score >= 30 ? 'low' : 'none';
    
    const matchedHTML = scheme.matched_criteria.length > 0 
        ? scheme.matched_criteria.map(c => `
            <li class="flex items-center gap-2 text-sm text-green-700">
                <i data-lucide="check" class="w-4 h-4"></i>
                ${c}
            </li>
        `).join('')
        : '<li class="text-sm text-gray-500">No matching criteria</li>';
    
    const missingHTML = scheme.missing_criteria.length > 0 
        ? scheme.missing_criteria.map(c => `
            <li class="flex items-start gap-2 text-sm text-red-700">
                <i data-lucide="x" class="w-4 h-4 mt-0.5 shrink-0"></i>
                ${c}
            </li>
        `).join('')
        : '';
    
    return `
        <div class="scheme-card ${statusClass} bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                    <h3 class="font-semibold text-gray-900 text-lg mb-1">${scheme.scheme_name}</h3>
                    <span class="status-badge ${statusClass}">${scheme.status}</span>
                </div>
                <div class="match-score ${scoreClass}">
                    ${scheme.match_score}%
                </div>
            </div>
            
            ${scheme.benefits ? `
                <p class="text-sm text-gray-600 mb-4">${scheme.benefits}</p>
            ` : ''}
            
            <div class="space-y-3">
                ${scheme.matched_criteria.length > 0 ? `
                    <div>
                        <p class="text-xs font-medium text-gray-500 uppercase mb-2">Matched Criteria</p>
                        <ul class="space-y-1">${matchedHTML}</ul>
                    </div>
                ` : ''}
                
                ${scheme.missing_criteria.length > 0 ? `
                    <div>
                        <p class="text-xs font-medium text-gray-500 uppercase mb-2">Missing Requirements</p>
                        <ul class="space-y-1">${missingHTML}</ul>
                    </div>
                ` : ''}
            </div>
            
            <div class="mt-4 pt-4 border-t border-gray-100 flex gap-2">
                ${scheme.application_url ? `
                    <a href="${scheme.application_url}" target="_blank" 
                       class="flex-1 text-center px-4 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 transition-colors">
                        Apply Now
                    </a>
                ` : ''}
                <button onclick="simplifyScheme(${JSON.stringify(scheme.scheme_name)}, ${JSON.stringify(scheme.description || '')})" 
                    class="px-4 py-2 text-primary-600 border border-primary-600 text-sm rounded-lg hover:bg-primary-50 transition-colors flex items-center gap-1">
                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                    Simplify
                </button>
            </div>
        </div>
    `;
}

// Mock data for demonstration when API is unavailable
function displayMockResults() {
    const mockData = {
        user_profile: userData,
        summary: {
            total_schemes: 12,
            eligible_count: 4,
            potential_count: 3,
            partial_count: 5
        },
        all_results: [
            {
                scheme_name: "Mai Bhago Vidya Scheme",
                match_score: 100,
                status: "Eligible",
                benefits: "Free bicycle worth Rs. 4,000 and school uniforms. Transportation support for rural girls.",
                matched_criteria: ["Age (18 years)", "Gender (Female)", "Occupation (Student)"],
                missing_criteria: [],
                description: "Free bicycles and uniforms for girl students in government schools from Class 6 to 12.",
                application_url: "https://punjab.gov.in/mai-bhago-vidya"
            },
            {
                scheme_name: "Post-Matric Scholarship",
                match_score: 95,
                status: "Eligible",
                benefits: "Full tuition fee reimbursement plus monthly maintenance allowance of Rs. 550-1200",
                matched_criteria: ["Category (SC)", "Age (18 years)", "Occupation (Student)"],
                missing_criteria: [],
                description: "Scholarship for SC/BC students pursuing post-matric education including diploma, degree, and professional courses.",
                application_url: "https://scholarships.punjab.gov.in"
            },
            {
                scheme_name: "Kanya Jagriti Jyoti Scheme",
                match_score: 90,
                status: "Eligible", 
                benefits: "Rs. 2,000 to Rs. 5,000 annual incentive based on class",
                matched_criteria: ["Category (SC)", "Gender (Female)", "Age (18 years)", "Occupation (Student)"],
                missing_criteria: [],
                description: "Financial incentive for SC/BC girl students to continue education and prevent dropouts.",
                application_url: "https://punjab.gov.in/kanya-jagriti"
            },
            {
                scheme_name: "Ashirwad Scheme",
                match_score: 85,
                status: "Potential",
                benefits: "Rs. 51,000 one-time grant for marriage expenses",
                matched_criteria: ["Category (SC)", "Gender (Female)", "Income (Below 3,27,90)"],
                missing_criteria: ["Age: Need to be 18+ for marriage assistance"],
                description: "Financial assistance for marriage of daughters from economically weaker sections and SC/BC categories.",
                application_url: "https://punjab.gov.in/ashirwad-scheme"
            },
            {
                scheme_name: "MMSBY Health Insurance",
                match_score: 75,
                status: "Potential",
                benefits: "Health coverage up to Rs. 10 Lakh per family per year. Cashless treatment in 800+ hospitals.",
                matched_criteria: ["Region (Punjab)", "Category (SC)"],
                missing_criteria: ["Income: Must be below Rs. 1,80,000"],
                description: "Mukhya Mantri Sehat Bima Yojana provides cashless health coverage for hospitalization in empanelled hospitals.",
                application_url: "https://sha.punjab.gov.in"
            },
            {
                scheme_name: "BOCW Education Stipend",
                match_score: 60,
                status: "Partial Match",
                benefits: "Rs. 8,000 to Rs. 12,000 annual stipend based on education level",
                matched_criteria: ["Age (18 years)", "Region (Punjab)"],
                missing_criteria: ["Occupation: Scheme is for Construction Worker children"],
                description: "Educational stipend for children of registered construction workers under Building and Other Construction Workers Board.",
                application_url: "https://pblabour.gov.in/bocw"
            },
            {
                scheme_name: "PM-Kisan Samman Nidhi",
                match_score: 40,
                status: "Partial Match",
                benefits: "Rs. 6,000 per year in three equal instalments of Rs. 2,000",
                matched_criteria: ["Region (Punjab)"],
                missing_criteria: ["Occupation: Scheme is for Farmer", "Land ownership required"],
                description: "Central government scheme providing direct income support to farmer families with cultivable land.",
                application_url: "https://pmkisan.gov.in"
            },
            {
                scheme_name: "Old Age Pension Scheme",
                match_score: 30,
                status: "Partial Match",
                benefits: "Rs. 1,500 per month pension directly to bank account",
                matched_criteria: ["Region (Punjab)"],
                missing_criteria: ["Age: Need to be at least 60 years", "Income: Must be below Rs. 60,000"],
                description: "Monthly pension for senior citizens from Below Poverty Line families and those without other income sources.",
                application_url: "https://punjab.gov.in/old-age-pension"
            }
        ]
    };
    
    showToast('Showing demo results with real Punjab schemes. Connect to backend for live matching.', 'info');
    displayResults(mockData);
}

// Document Tracker
function initializeDocumentTracker() {
    const checklist = document.getElementById('documentChecklist');
    if (!checklist) return;
    
    const html = commonDocuments.map(doc => `
        <label class="doc-checkbox flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
            <input type="checkbox" value="${doc.id}" onchange="updateUserDocuments(this)" 
                class="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500">
            <i data-lucide="${doc.icon}" class="w-5 h-5 text-gray-400"></i>
            <span class="text-sm font-medium text-gray-700">${doc.name}</span>
            ${doc.expiry ? '<span class="ml-auto text-xs text-amber-600 bg-amber-100 px-2 py-0.5 rounded">Expires</span>' : ''}
        </label>
    `).join('');
    
    checklist.innerHTML = html;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function updateUserDocuments(checkbox) {
    if (checkbox.checked) {
        userDocuments.push(checkbox.value);
    } else {
        userDocuments = userDocuments.filter(d => d !== checkbox.value);
    }
}

function checkDocumentEligibility() {
    if (userDocuments.length === 0) {
        showToast('Please select at least one document', 'warning');
        return;
    }
    
    // Show document match results
    const resultsDiv = document.getElementById('documentResults');
    resultsDiv.classList.remove('hidden');
    
    // Map user document IDs to names
    const userDocNames = userDocuments.map(id => {
        const doc = commonDocuments.find(d => d.id === id);
        return doc ? doc.name : id;
    });
    
    resultsDiv.innerHTML = `
        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h4 class="font-semibold text-green-800 mb-2">Documents You Have (${userDocuments.length})</h4>
            <ul class="space-y-1">
                ${userDocNames.map(name => `
                    <li class="flex items-center gap-2 text-sm text-green-700">
                        <i data-lucide="check-circle" class="w-4 h-4"></i>
                        ${name}
                    </li>
                `).join('')}
            </ul>
        </div>
        <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-sm text-blue-800">
                <strong>Tip:</strong> Complete the eligibility form to see which schemes match your documents.
            </p>
        </div>
    `;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Deadline Alerts
async function loadDeadlineAlerts() {
    const contentDiv = document.getElementById('deadlineContent');
    if (!contentDiv) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/deadline-alerts?days=30`);
        
        if (!response.ok) {
            throw new Error('Failed to load deadline alerts');
        }
        
        const data = await response.json();
        displayDeadlineAlerts(data.urgent_schemes);
        
    } catch (error) {
        // Display mock deadline data
        displayDeadlineAlerts([
            {
                'Scheme Name': 'Post-Matric Scholarship',
                'Application Deadline': '2026-04-15',
                'Benefits': 'Full tuition fee reimbursement for SC/BC students'
            },
            {
                'Scheme Name': 'BOCW Education Stipend',
                'Application Deadline': '2026-04-30',
                'Benefits': 'Rs. 8,000-12,000 annual stipend for students'
            },
            {
                'Scheme Name': 'Ashirwad Scheme',
                'Application Deadline': '2026-05-15',
                'Benefits': 'Rs. 51,000 marriage assistance'
            }
        ]);
    }
}

function displayDeadlineAlerts(schemes) {
    const contentDiv = document.getElementById('deadlineContent');
    if (!contentDiv) return;
    
    if (schemes.length === 0) {
        contentDiv.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i data-lucide="calendar-check" class="w-12 h-12 mx-auto mb-4 opacity-50"></i>
                <p>No urgent deadlines in the next 30 days</p>
            </div>
        `;
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        return;
    }
    
    const html = schemes.map(scheme => {
        const deadline = new Date(scheme['Application Deadline']);
        const today = new Date();
        const daysLeft = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
        const urgency = daysLeft <= 7 ? 'urgent' : daysLeft <= 14 ? 'warning' : 'normal';
        
        return `
            <div class="deadline-card ${urgency} bg-white rounded-lg p-4 shadow-sm">
                <div class="flex items-start justify-between">
                    <div>
                        <h3 class="font-semibold text-gray-900">${scheme['Scheme Name']}</h3>
                        <p class="text-sm text-gray-600 mt-1">${scheme['Benefits'] || ''}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-2xl font-bold ${urgency === 'urgent' ? 'text-red-600' : urgency === 'warning' ? 'text-amber-600' : 'text-green-600'}">
                            ${daysLeft}
                        </p>
                        <p class="text-xs text-gray-500">days left</p>
                    </div>
                </div>
                <div class="mt-3 flex items-center justify-between">
                    <span class="text-sm text-gray-500">
                        <i data-lucide="calendar" class="w-4 h-4 inline mr-1"></i>
                        Deadline: ${deadline.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </span>
                    <button onclick="addToCalendar('${scheme['Scheme Name']}', '${scheme['Application Deadline']}')" 
                        class="text-sm text-primary-600 hover:underline flex items-center gap-1">
                        <i data-lucide="calendar-plus" class="w-4 h-4"></i>
                        Add to Calendar
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    contentDiv.innerHTML = html;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function addToCalendar(schemeName, deadline) {
    const date = new Date(deadline);
    const startDate = date.toISOString().replace(/-|:|\.\d+/g, '').slice(0, 15) + 'Z';
    const endDate = startDate;
    
    const googleCalendarUrl = `https://www.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(schemeName + ' Deadline')}&dates=${startDate}/${endDate}&details=${encodeURIComponent('Application deadline for ' + schemeName + ' scheme. Apply via SchemeScout.')}`;
    
    window.open(googleCalendarUrl, '_blank');
    showToast('Opening Google Calendar...', 'success');
}

// AI Simplify
async function simplifyScheme(schemeName, description) {
    showToast('Simplifying scheme details...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/simplify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scheme_name: schemeName,
                text: description || schemeName
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to simplify');
        }
        
        const data = await response.json();
        showSimplifiedModal(schemeName, data.simplified);
        
    } catch (error) {
        // Show a simplified version locally
        showSimplifiedModal(schemeName, {
            summary: description || 'Government welfare scheme for eligible citizens of Punjab.',
            ai_powered: false
        });
    }
}

function showSimplifiedModal(schemeName, simplified) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    // Generate content based on whether we have TL;DR points or just raw text
    let contentHTML = '';
    
    if (simplified.tldr_points && simplified.tldr_points.length > 0) {
        // Display structured TL;DR points
        const icons = ['gift', 'users', 'file-text'];
        contentHTML = simplified.tldr_points.map((point, index) => {
            const icon = icons[index] || 'check-circle';
            return `
                <div class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <div class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <i data-lucide="${icon}" class="w-4 h-4 text-primary-600"></i>
                    </div>
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-900 mb-1">${point.split(':')[0] || 'Point'}</p>
                        <p class="text-sm text-gray-600">${point.split(':').slice(1).join(':').trim() || point}</p>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        // Fallback to raw text display
        contentHTML = `
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-700">${simplified.raw_response || simplified.summary}</p>
            </div>
        `;
    }
    
    modal.innerHTML = `
        <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl">
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h3 class="text-xl font-bold text-gray-900">${schemeName}</h3>
                    <span class="text-xs ${simplified.ai_powered ? 'text-primary-600' : 'text-gray-500'}">
                        ${simplified.ai_powered ? 'AI-Powered TL;DR' : 'Basic Summary'}
                    </span>
                </div>
                <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                    <i data-lucide="x" class="w-6 h-6"></i>
                </button>
            </div>
            
            <div class="space-y-3 mb-6">
                ${contentHTML}
            </div>
            
            <div class="mt-6 flex gap-3">
                <button onclick="this.closest('.fixed').remove()" 
                    class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Section Navigation
function showSection(sectionId) {
    // Hide all main sections
    const sections = ['hero', 'eligibility-form', 'results', 'deadline-alerts', 'document-tracker'];
    sections.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    });
    
    // Show requested section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.remove('hidden');
    }
    
    // Show hero and form together
    if (sectionId === 'eligibility-form') {
        document.getElementById('hero').classList.remove('hidden');
    }
    
    // Reinitialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Reset Form
function resetForm() {
    document.getElementById('schemeForm').reset();
    currentStep = 1;
    
    // Hide all steps except first
    for (let i = 2; i <= totalSteps; i++) {
        document.getElementById(`step${i}`).classList.add('hidden');
    }
    document.getElementById('step1').classList.remove('hidden');
    
    updateProgressBar();
    updateNavigationButtons();
    
    // Show form, hide results
    showSection('eligibility-form');
}

// Form Validation
function setupValidation() {
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.required && !this.value.trim()) {
                this.classList.add('border-red-500');
            } else {
                this.classList.remove('border-red-500');
                if (this.value.trim()) {
                    this.classList.add('border-green-500');
                }
            }
        });
        
        input.addEventListener('input', function() {
            this.classList.remove('border-red-500');
        });
    });
}

// Utility Functions
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.toggle('hidden', !show);
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!toast || !toastMessage) return;
    
    // Set message and style
    toastMessage.textContent = message;
    toast.className = 'fixed bottom-4 right-4 px-6 py-4 rounded-lg shadow-xl z-50 transition-all';
    
    switch (type) {
        case 'success':
            toast.classList.add('bg-green-600', 'text-white');
            break;
        case 'error':
            toast.classList.add('bg-red-600', 'text-white');
            break;
        case 'warning':
            toast.classList.add('bg-amber-500', 'text-white');
            break;
        default:
            toast.classList.add('bg-gray-900', 'text-white');
    }
    
    // Show toast
    toast.classList.remove('hidden');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Export functions for global access
window.changeStep = changeStep;
window.resetForm = resetForm;
window.showSection = showSection;
window.updateUserDocuments = updateUserDocuments;
window.checkDocumentEligibility = checkDocumentEligibility;
window.simplifyScheme = simplifyScheme;
window.addToCalendar = addToCalendar;
