// more data 
// --- 1. USER DATA STATE ---
let userData = {
    gender: "",
    age: "19",
    maritalStatus: "N/A",
    state: "Punjab",
    category: "General",
    disability: "No",
    occupation: "",
    minority: "No",
    documents: []
};

// --- 2. MASTER SCHEME DATABASE (Aapke Naye Excel Data se) ---
const schemeDatabase = [
    {
        name: "Punjab Green Tractors Scheme",
        occupation: "Farmer", gender: "All", state: "Punjab", ageMin: 25,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook"],
        desc: "Farmers purchasing or leasing tractors get 0.50 subsidy per tractor."
    },
    {
        name: "Agri-Entrepreneur Unit Setup Grant",
        occupation: "Entrepreneur", gender: "All", state: "Punjab", ageMin: 18,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook", "Business plan", "Domicile certificate"],
        desc: "Grant of ₹1,00,000 for setting up agri-processing units."
    },
    {
        name: "Punjab Organic Farming Promotion Scheme",
        occupation: "Farmer", gender: "All", state: "Punjab", ageMin: 30,
        requiredDocs: ["Aadhar card", "Bank passbook", "Domicile certificate", "Organic certification application"],
        desc: "Incentives for farmers switching to certified organic practices."
    },
    {
        name: "Horticulture Development Scheme (Fruit Crops)",
        occupation: "Farmer", gender: "All", state: "Punjab", ageMin: 25,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook", "Sapling-purchase invoice"],
        desc: "₹5,000 per acre for planting fruit trees or expanding orchards."
    },
    {
        name: "Punjab Livestock Card Scheme",
        occupation: "Farmer", gender: "All", state: "Punjab", ageMin: 20,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook", "Animal health record"],
        desc: "Subsidised feed, vaccination, and equipment for dairy/poultry farmers."
    },
    {
        name: "Agri-Graduate Internship for Rural Youth",
        occupation: "Student", gender: "All", state: "Punjab", ageMin: 20,
        requiredDocs: ["Aadhar card", "Degree certificate", "Bank passbook", "College internship letter"],
        desc: "₹8,000 per month stipend for Agriculture graduates working in rural farms."
    },
    {
        name: "Solar-Powered Tube-Well Scheme",
        occupation: "Farmer", gender: "All", state: "Punjab", ageMin: 25,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook", "Electricity bill"],
        desc: "Subsidy for replacing electric tube-wells with solar-powered ones."
    },
    {
        name: "Punjab Women-Farmer Equity Grant",
        occupation: "Farmer", gender: "Female", state: "Punjab", ageMin: 25,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook", "Domicile certificate"],
        desc: "₹15,000 direct cash grant for women landowners or co-farmers."
    },
    {
        name: "Punjab Youth Agri-Entrepreneur Scheme",
        occupation: "Entrepreneur", gender: "All", state: "Punjab", ageMin: 18,
        requiredDocs: ["Aadhar card", "Income certificate", "Bank passbook", "Business plan", "Educational certificate"],
        desc: "₹1,20,000 grant for youth aged 18-30 starting agri-businesses."
    },
    {
        name: "Punjab Ghar Ghar Ration Yojana",
        occupation: "All", gender: "All", state: "Punjab", ageMin: 19,
        requiredDocs: ["Aadhar card", "Ration card", "Income certificate", "Residence proof"],
        desc: "Doorstep delivery of subsidised or free ration."
    },
    {
        name: "Ashirwad Scheme",
        occupation: "All", gender: "Female", state: "Punjab", ageMin: 18,
        requiredDocs: ["Aadhar card", "Age proof", "Income certificate"],
        desc: "Financial assistance (₹15,000 to ₹21,000) for marriage of girls from SC/BC families."
    }
];

// --- 3. BUTTONS & UI LOGIC ---

function selectGender(el, val) {
    document.querySelectorAll('#step1 .option-card').forEach(s => s.classList.remove('selected'));
    el.classList.add('selected');
    userData.gender = val;
    checkMaritalStatus();
}

function selectOption(el, val, field) {
    let siblings = el.parentElement.querySelectorAll('.option-card');
    siblings.forEach(s => s.classList.remove('selected'));
    el.classList.add('selected');
    userData[field] = val;
}

function handleDisability(el, isYes) {
    userData.disability = isYes ? "Yes" : "No";
    let siblings = el.parentElement.querySelectorAll('.option-card');
    siblings.forEach(s => s.classList.remove('selected'));
    el.classList.add('selected');
    let field = document.getElementById('disabilityField');
    if (field) field.style.display = isYes ? 'block' : 'none';
}

function checkMaritalStatus() {
    let ageVal = parseInt(document.getElementById('ageInput').value) || 0;
    userData.age = ageVal;
    let sec = document.getElementById('maritalStatusSection');
    if (sec) {
        sec.style.display = (userData.gender === 'Female' && ageVal >= 19) ? 'block' : 'none';
    }
}

function nextStep(n) {
    if (n === 3) {
        const stateEl = document.getElementById('stateSelect');
        if(stateEl) userData.state = stateEl.value;
    }
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    let target = document.getElementById('step' + n);
    if (target) target.classList.add('active');
}

function prevStep(n) { nextStep(n); }

// --- 4. FINISH & RESULTS ---

function saveDataAndDownload() {
    const docCheckboxes = document.querySelectorAll('.doc-check');
    userData.documents = Array.from(docCheckboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    findEligibleSchemes();
}

function findEligibleSchemes() {
    const userAge = parseInt(userData.age);

    const results = schemeDatabase.map(scheme => {
        // Strict Matching Logic
        const isProfileFit = (scheme.occupation === userData.occupation || scheme.occupation === "All") &&
                             (scheme.gender === userData.gender || scheme.gender === "All") &&
                             (scheme.state === userData.state || scheme.state === "All") &&
                             (userAge >= scheme.ageMin);

        const missing = scheme.requiredDocs.filter(d => !userData.documents.includes(d));

        return { 
            ...scheme, 
            isFit: isProfileFit, 
            missingDocs: missing, 
            isEligible: isProfileFit && missing.length === 0 
        };
    });

    displayResults(results);
}

function displayResults(data) {
    const container = document.querySelector('.form-container');
    let html = `<h2 style="color:#ffcc00; text-align:center;">Recommended for You</h2>`;

    const filtered = data.filter(s => s.isFit);

    if (filtered.length === 0) {
        html += `<p style="color:red; text-align:center; padding:20px;">No schemes found for your current profile.</p>`;
    } else {
        filtered.forEach(s => {
            const color = s.isEligible ? "#4caf50" : "#f9a825";
            html += `
                <div style="background:white; color:#333; padding:15px; border-radius:12px; margin-bottom:15px; border-left:6px solid ${color}; text-align:left; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:#107c41;">${s.name}</h3>
                    <p style="font-size:12px; margin:5px 0; color:#555;">${s.desc}</p>
                    ${s.isEligible ? 
                        `<p style="color:green; font-weight:bold; font-size:13px; margin-top:10px;">✔ Yes, you are eligible to apply!</p>` : 
                        `<p style="color:#d32f2f; font-size:12.5px; margin-top:8px;"><b>These documents are needed for eligibility:</b><br>• ${s.missingDocs.join("<br>• ")}</p>`
                    }
                </div>`;
        });
    }

    html += `<button onclick="location.reload()" class="next-btn" style="margin-top:10px;">Restart Check</button>`;
    container.innerHTML = html;
}