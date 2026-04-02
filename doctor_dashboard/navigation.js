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
                <img class="h-full w-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBizfKe_xyPrdy-5TAjyCwRALgQQcQJRmmj2VFhxrCkO5NhY7CdU4gDDVE4ULBx4fD8KZc-pbr-WzJHgtHWrmjaiAdB3DP-ki2e-DyKPHH6ueyLOZzOyLU4Mhr3k70ficKI-bBAoZjmWlvsBod_-bEL8q-JCukgp7-o0NdNZtrULmlB1Y0F08b4Wu7i9H2-Fag86z_zQFyISxn6tF1fxuFdFTXVp4Cmcj-LBXSKA_37Z5ljp-61xRhmEen__w-Sl6COyvt0miEeOYk"/>
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
        // make sure it has standard classes
        if (!el.classList.contains('bg-zinc-50')) {
            el.className = "hidden md:flex h-screen w-72 border-r border-zinc-200/50 dark:border-zinc-800/50 flex-col p-4 gap-2 bg-zinc-50 dark:bg-zinc-950";
        }
    });

    // Mobile nav
    const mobileNavDisplays = document.querySelectorAll('.kb-mobile-nav');
    mobileNavDisplays.forEach(el => {
        let mobileHtml = '';
        const mNavItems = [
            { href: '/index.html', icon: 'favorite', text: 'Twin', roles: ['doctor'] },
            { href: '/correlations.html', icon: 'analytics', text: 'Stats', roles: ['doctor'] },
            { href: '/patients.html', icon: 'supervisor_account', text: 'Patients', roles: ['doctor'] },
            { href: '/admin.html', icon: 'admin_panel_settings', text: 'Requests', roles: ['admin'] },
            { href: '/admin.html#doctors-section', icon: 'medical_services', text: 'Doctors', roles: ['admin'] },
            { href: '/admin.html#patients-section', icon: 'person', text: 'Patients', roles: ['admin'] },
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
    
    let headerContent = '';
    
    if (titleOverride) {
        // Admin or Settings page without patient context required
        headerContent = `
        <div class="flex items-center gap-4">
            <h2 class="font-headline font-bold text-xl text-on-surface">${titleOverride}</h2>
        </div>
        `;
    } else if (patientName && medicalId) {
        headerContent = `
        <div class="flex items-center gap-4">
            <div class="h-10 w-10 rounded-full border-2 border-primary-container overflow-hidden">
                <img class="h-full w-full object-cover" src="https://ui-avatars.com/api/?name=${encodeURIComponent(patientName)}&background=da3433&color=fff"/>
            </div>
            <div class="font-['Manrope'] font-bold tracking-tight text-lg text-on-surface">
                Patient: ${patientName} <span class="text-on-surface-variant font-medium text-sm ml-2">ID: ${medicalId}</span>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <div class="flex items-center gap-2 px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full hidden sm:flex">
                <span class="material-symbols-outlined text-sm">cloud_done</span>
                <span class="text-[10px] font-bold uppercase tracking-widest">Sync Active</span>
            </div>
            <!-- Removed offline cloud icon as requested -->
        </div>
        `;
    } else {
        headerContent = `
        <div class="flex items-center gap-4">
            <h2 class="font-headline font-bold text-xl text-on-surface">Please select a patient</h2>
        </div>
        `;
    }

    const headerDisplays = document.querySelectorAll('.kb-header');
    headerDisplays.forEach(el => {
        el.innerHTML = headerContent;
        // set standard class
        if (!el.classList.contains('h-16')) {
            el.className = "fixed top-0 w-full z-40 md:relative bg-white/60 dark:bg-zinc-900/60 backdrop-blur-xl flex justify-between items-center px-6 h-16 shadow-[0_20px_40px_rgba(186,26,32,0.08)] border-b border-zinc-100";
        }
    });
}
