export function renderNavigation() {
    const docName = localStorage.getItem('doctor_name') || 'Dr. Unknown';
    const role = localStorage.getItem('doctor_role') || 'doctor';
    const path = window.location.pathname;

    const navItems = [
        { href: '/index.html', icon: 'dashboard', text: 'Patient Overview', roles: ['doctor'] },
        { href: '/patients.html', icon: 'supervisor_account', text: 'Patients', roles: ['doctor'] },
        { href: '/correlations.html', icon: 'timeline', text: 'Correlations', roles: ['doctor'] },
        { href: '/ai-diagnostics.html', icon: 'psychology', text: 'AI Diagnostics', roles: ['doctor'] },
        { href: '/admin.html', icon: 'admin_panel_settings', text: 'Requests', roles: ['admin'] },
        { href: '/admin.html#doctors-section', icon: 'medical_services', text: 'Doctors', roles: ['admin'] },
        { href: '/admin.html#patients-section', icon: 'person', text: 'Patients', roles: ['admin'] },
        { href: '/settings.html', icon: 'settings', text: 'Settings', roles: ['doctor', 'admin'] }
    ];

    let navHtml = '';
    navItems.forEach(item => {
        if (!item.roles.includes(role)) return;
        
        const isActive = path === item.href || (path === '/' && item.href === '/index.html');
        
        if (isActive) {
            navHtml += `
            <a class="bg-white dark:bg-zinc-900 text-red-600 dark:text-red-400 shadow-sm rounded-xl font-bold flex items-center gap-3 px-4 py-3 transition-all duration-200 translate-x-1" href="${item.href}">
                <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">${item.icon}</span>
                <span class="font-['Plus_Jakarta_Sans'] font-medium text-sm">${item.text}</span>
            </a>`;
        } else {
            navHtml += `
            <a class="text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 flex items-center gap-3 px-4 py-3 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50 rounded-xl transition-all" href="${item.href}">
                <span class="material-symbols-outlined">${item.icon}</span>
                <span class="font-['Plus_Jakarta_Sans'] font-medium text-sm">${item.text}</span>
            </a>`;
        }
    });

    const sidebarContent = `
    <div class="font-['Manrope'] font-extrabold text-2xl text-red-700 mb-8 px-4 mt-2 cursor-default">
        KeepBeat
    </div>
    <nav class="flex flex-col gap-2 flex-grow">
        ${navHtml}
    </nav>
    <div class="mt-auto p-4 bg-surface-container rounded-2xl flex flex-col gap-4">
        <div class="flex items-center gap-4">
            <div class="h-10 w-10 rounded-full overflow-hidden bg-zinc-300">
                <img class="h-full w-full object-cover" src="https://ui-avatars.com/api/?name=${encodeURIComponent(docName)}&background=f0f1f2&color=b6171e"/>
            </div>
            <div>
                <p id="doctor-name-display" class="font-['Plus_Jakarta_Sans'] font-bold text-sm text-on-surface">${docName}</p>
                <p class="font-['Inter'] text-[10px] text-on-surface-variant uppercase tracking-wider">${role === 'admin' ? 'System Admin' : 'Cardiology'}</p>
            </div>
        </div>
        <button onclick="localStorage.clear(); window.location.href='/login.html'" class="w-full flex items-center justify-center gap-2 py-2 border border-zinc-200 dark:border-zinc-700/50 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
            <span class="material-symbols-outlined text-[16px]">logout</span>
            <span class="font-['Plus_Jakarta_Sans'] font-bold text-xs uppercase tracking-wider">Logout</span>
        </button>
    </div>
    `;

    const sidebarDisplays = document.querySelectorAll('.kb-sidebar');
    sidebarDisplays.forEach(el => {
        el.innerHTML = sidebarContent;
        if (!el.classList.contains('bg-zinc-50')) {
            el.className = "hidden md:flex h-screen w-72 border-r border-zinc-200/50 dark:border-zinc-800/50 flex-col p-4 gap-2 bg-zinc-50 dark:bg-zinc-950 flex-shrink-0";
        }
    });

    const mobileNavDisplays = document.querySelectorAll('.kb-mobile-nav');
    mobileNavDisplays.forEach(el => {
        let mobileHtml = '';
        const mNavItems = [
            { href: '/index.html', icon: 'favorite', text: 'Twin', roles: ['doctor'] },
            { href: '/correlations.html', icon: 'analytics', text: 'Stats', roles: ['doctor'] },
            { href: '/patients.html', icon: 'supervisor_account', text: 'Patients', roles: ['doctor'] },
            { href: '/admin.html', icon: 'admin_panel_settings', text: 'Requests', roles: ['admin'] },
            { href: '/settings.html', icon: 'settings', text: 'Settings', roles: ['doctor', 'admin'] }
        ].filter(item => item.roles.includes(role));

        mNavItems.forEach(item => {
            const isActive = path === item.href || (path === '/' && item.href === '/index.html');
            if (isActive) {
                mobileHtml += `
                <a class="flex flex-col items-center justify-center bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400 rounded-2xl px-5 py-2 scale-95 duration-200" href="${item.href}">
                    <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">${item.icon}</span>
                    <span class="font-['Inter'] font-semibold text-[10px] uppercase tracking-wider mt-1">${item.text}</span>
                </a>`;
            } else {
                mobileHtml += `
                <a class="flex flex-col items-center justify-center text-zinc-400 dark:text-zinc-600 px-5 py-2 hover:text-red-500 transition-colors" href="${item.href}">
                    <span class="material-symbols-outlined">${item.icon}</span>
                    <span class="font-['Inter'] font-semibold text-[10px] uppercase tracking-wider mt-1">${item.text}</span>
                </a>`;
            }
        });

        el.innerHTML = mobileHtml;
        el.className = "md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-2 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-2xl rounded-t-[2rem] h-20 shadow-[0_-10px_30px_rgba(0,0,0,0.05)]";
    });
}

export function renderHeader(titleOverride = null) {
    const patientName = localStorage.getItem('selectedPatientName');
    const medicalId = localStorage.getItem('selectedPatientMedicalId');
    const docId = localStorage.getItem('doctor_id');
    const path = window.location.pathname;
    
    // Check if patient context is required
    const isPatientRequired = path === '/' || path === '/index.html' || path === '/correlations.html' || path === '/ai-diagnostics.html';
    
    if (isPatientRequired && !patientName && docId) {
        // Trigger modal immediately if no patient selected
        setTimeout(() => showPatientSelector(true), 100);
    }

    let headerContent = '';
    if (titleOverride) {
        headerContent = `
        <div class="flex items-center gap-4">
            <h2 class="font-headline font-bold text-xl text-on-surface">${titleOverride}</h2>
        </div>
        `;
    } else if (patientName && medicalId) {
        headerContent = `
        <div class="flex items-center gap-4 cursor-pointer group" id="header-patient-context">
            <div class="h-10 w-10 rounded-full border-2 border-primary-container overflow-hidden group-hover:scale-110 transition-transform">
                <img class="h-full w-full object-cover" src="https://ui-avatars.com/api/?name=${encodeURIComponent(patientName)}&background=da3433&color=fff"/>
            </div>
            <div class="font-['Manrope'] font-bold tracking-tight text-lg text-on-surface">
                Patient: <span class="group-hover:text-primary transition-colors">${patientName}</span> <span class="text-on-surface-variant font-medium text-sm ml-2">ID: ${medicalId}</span>
            </div>
            <span class="material-symbols-outlined text-zinc-400 group-hover:text-primary transition-all text-sm">expand_more</span>
        </div>
        <div class="flex items-center gap-3">
            <div class="flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full hidden sm:flex border border-emerald-100">
                <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">verified</span>
                <span class="text-[10px] font-bold uppercase tracking-widest">Twin Active</span>
            </div>
        </div>
        `;
    } else {
        headerContent = `
        <div class="flex items-center gap-4 cursor-pointer group" id="header-select-trigger">
            <div class="h-10 w-10 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-400 group-hover:bg-primary/10 group-hover:text-primary transition-all">
                <span class="material-symbols-outlined">person_search</span>
            </div>
            <h2 class="font-headline font-bold text-xl text-zinc-400 group-hover:text-on-surface transition-colors">Select Patient Context</h2>
        </div>
        `;
    }

    const headerDisplays = document.querySelectorAll('.kb-header');
    headerDisplays.forEach(el => {
        el.innerHTML = headerContent;
        if (!el.classList.contains('h-16')) {
            el.className = "fixed top-0 w-full z-40 md:relative bg-white/60 dark:bg-zinc-900/60 backdrop-blur-xl flex justify-between items-center px-6 h-16 shadow-[0_20px_40px_rgba(186,26,32,0.08)] border-b border-zinc-100";
        }
    });

    // Rebind events since we replaced innerHTML
    const selectTrigger = document.getElementById('header-select-trigger');
    if (selectTrigger) selectTrigger.onclick = () => showPatientSelector(true);
    
    const contextTrigger = document.getElementById('header-patient-context');
    if (contextTrigger) contextTrigger.onclick = () => showPatientSelector(false);
}

export async function showPatientSelector(isMandatory = false) {
    const docId = localStorage.getItem('doctor_id');
    if (!docId) return;

    // Remove existing modal if any
    const existing = document.getElementById('patient-selector-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'patient-selector-modal';
    modal.className = "fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-md bg-zinc-950/40 animate-in fade-in duration-300";
    
    modal.innerHTML = `
        <div class="bg-white dark:bg-zinc-900 rounded-[2.5rem] shadow-2xl w-full max-w-2xl overflow-hidden border border-white/20 flex flex-col scale-95 animate-in zoom-in duration-300">
            <div class="px-10 py-8 border-b border-zinc-100 dark:border-zinc-800 flex justify-between items-center bg-zinc-50/50 dark:bg-zinc-950/20">
                <div>
                    <h3 class="font-headline font-extrabold text-2xl text-on-surface">Clinical Context</h3>
                    <p class="text-sm font-medium text-zinc-500 mt-1">Select a patient to initialize the Digital Twin telemetry stream.</p>
                </div>
                ${!isMandatory ? `
                <button id="close-modal-btn" class="h-10 w-10 flex items-center justify-center rounded-full bg-white dark:bg-zinc-800 text-zinc-400 hover:text-zinc-700 transition-colors shadow-sm">
                    <span class="material-symbols-outlined">close</span>
                </button>` : ''}
            </div>
            
            <div class="p-10 max-h-[60vh] overflow-y-auto" id="patient-grid">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div class="h-24 bg-zinc-100 animate-pulse rounded-2xl"></div>
                    <div class="h-24 bg-zinc-100 animate-pulse rounded-2xl"></div>
                </div>
            </div>

            <div class="px-10 py-6 border-t border-zinc-100 dark:border-zinc-800 bg-zinc-50/30 text-center">
                <p class="text-xs font-bold text-zinc-400 uppercase tracking-widest">Verified Digital Twin Environment v2.4</p>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    const closeBtn = document.getElementById('close-modal-btn');
    if (closeBtn) closeBtn.onclick = () => modal.remove();

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/patients?doctor_id=${docId}`);
        const patients = await res.json();
        const grid = document.getElementById('patient-grid');
        
        if (patients.length === 0) {
            grid.innerHTML = `<div class="text-center py-10"><p class="font-bold text-zinc-500">No patients enrolled.</p><a href="/patients.html" class="text-primary font-bold text-sm mt-2 block hover:underline">Enroll patients in Patient Management</a></div>`;
            return;
        }

        grid.innerHTML = `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                ${patients.map(p => `
                    <div data-id="${p.id}" data-name="${p.full_name}" data-medical="${p.medical_id}" class="patient-card p-5 rounded-3xl border border-zinc-100 dark:border-zinc-800 hover:border-primary/30 hover:bg-primary/5 cursor-pointer transition-all group flex items-center gap-4 bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md">
                        <div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold group-hover:scale-110 transition-transform">${p.full_name.charAt(0)}</div>
                        <div class="flex-grow">
                            <p class="font-headline font-bold text-on-surface group-hover:text-primary transition-colors">${p.full_name}</p>
                            <p class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">${p.medical_id}</p>
                        </div>
                        <span class="material-symbols-outlined text-zinc-200 group-hover:text-primary opacity-0 group-hover:opacity-100 transition-all">chevron_right</span>
                    </div>
                `).join('')}
            </div>
        `;

        // Bind selection events
        grid.querySelectorAll('.patient-card').forEach(card => {
            card.onclick = () => {
                const { id, name, medical } = card.dataset;
                localStorage.setItem('selectedPatientId', id);
                localStorage.setItem('selectedPatientName', name);
                localStorage.setItem('selectedPatientMedicalId', medical);
                modal.remove();
                renderHeader();
                window.location.reload(); 
            };
        });

    } catch (err) {
        document.getElementById('patient-grid').innerHTML = `<p class="text-red-500 text-center font-bold">Failed to load patients. Check server connection.</p>`;
    }
}
