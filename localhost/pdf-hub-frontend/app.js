// ===== Sidebar =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleIcon = document.getElementById('toggleIcon');
    sidebar.classList.toggle('collapsed');
    
    // Update toggle icon
    if (sidebar.classList.contains('collapsed')) {
        toggleIcon.className = 'bi bi-chevron-right';
    } else {
        toggleIcon.className = 'bi bi-chevron-left';
    }
}

// Close sidebar on mobile when clicking outside
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('menuBtn');
    
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

// Toggle sidebar on mobile
document.getElementById('menuBtn').addEventListener('click', (e) => {
    e.stopPropagation();
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
});

// ===== Navigation =====
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('open');
        }
        
        // Handle page navigation
        const page = this.dataset.page;
        console.log('Navigating to:', page);
        // Add your page navigation logic here
    });
});

// ===== PDF Converter Logic =====
const API_BASE = 'http://localhost:5000/api';
let uploadedFiles = [];
let currentMode = 'convert';

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const processBtn = document.getElementById('processBtn');
const clearBtn = document.getElementById('clearBtn');
const fileName = document.getElementById('fileName');
const status = document.getElementById('status');
const fileTypes = document.getElementById('fileTypes');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressLabel = document.getElementById('progressLabel');
const progressPercent = document.getElementById('progressPercent');

// Mode switching
function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
    if (mode === 'convert') {
        fileTypes.innerHTML = '<i class="bi bi-check-circle-fill"></i> Supports: JPG, PNG, BMP, GIF, TIFF, WEBP';
        processBtn.innerHTML = '<i class="bi bi-play-fill"></i> Convert Now';
    } else {
        fileTypes.innerHTML = '<i class="bi bi-check-circle-fill"></i> Supports: PDF files only';
        processBtn.innerHTML = '<i class="bi bi-play-fill"></i> Merge Now';
    }
    
    clearFiles();
}

// Drag and Drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// Handle files
function handleFiles(files) {
    const validFiles = Array.from(files).filter(file => {
        if (currentMode === 'convert') {
            const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/tiff', 'image/webp'];
            return validTypes.includes(file.type);
        } else {
            return file.name.toLowerCase().endsWith('.pdf');
        }
    });
    
    if (validFiles.length === 0) {
        showStatus('Invalid file type. Please upload the correct files.', 'error');
        return;
    }
    
    uploadedFiles = [...uploadedFiles, ...validFiles];
    renderFileList();
    showStatus(`${uploadedFiles.length} file(s) uploaded successfully`, 'success');
}

// Render file list
function renderFileList() {
    if (uploadedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }
    
    fileList.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <i class="bi ${currentMode === 'convert' ? 'bi-image' : 'bi-file-pdf'} file-icon"></i>
            <span class="file-name">${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
            <button class="remove-btn" data-index="${index}">
                <i class="bi bi-x-circle"></i>
            </button>
        </div>
    `).join('');
    
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.closest('.remove-btn').dataset.index);
            uploadedFiles.splice(index, 1);
            renderFileList();
            if (uploadedFiles.length === 0) showStatus('', '');
        });
    });
}

// Update progress
function updateProgress(percent, label) {
    progressFill.style.width = percent + '%';
    progressPercent.textContent = percent + '%';
    if (label) progressLabel.textContent = label;
}

// Show/hide progress
function showProgress(show) {
    progressContainer.style.display = show ? 'block' : 'none';
}

// Process files
processBtn.addEventListener('click', async () => {
    if (uploadedFiles.length === 0) {
        showStatus('Please upload at least one file', 'error');
        return;
    }
    
    const formData = new FormData();
    uploadedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    const name = fileName.value.trim();
    if (name) formData.append('filename', name);
    
    try {
        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
        showStatus('', '');
        showProgress(true);
        updateProgress(0, 'Starting...');
        
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 15 + 5;
            if (progress > 90) progress = 90;
            updateProgress(Math.min(progress, 90), 'Processing your files...');
        }, 200);
        
        const endpoint = currentMode === 'convert' ? 'convert' : 'merge';
        const response = await fetch(`${API_BASE}/${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Processing failed');
        }
        
        updateProgress(100, 'Complete!');
        showStatus('<i class="bi bi-check-circle-fill"></i> File processed successfully!', 'success');
        
        // Download
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const defaultName = currentMode === 'convert' ? 'converted.pdf' : 'merged.pdf';
        a.download = name ? `${name}.pdf` : defaultName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        setTimeout(() => {
            showProgress(false);
            clearFiles();
        }, 1500);
        
    } catch (error) {
        showProgress(false);
        showStatus('<i class="bi bi-exclamation-triangle-fill"></i> ' + error.message, 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = currentMode === 'convert' ? 
            '<i class="bi bi-play-fill"></i> Convert Now' : 
            '<i class="bi bi-play-fill"></i> Merge Now';
    }
});

// Clear files
clearBtn.addEventListener('click', clearFiles);

function clearFiles() {
    uploadedFiles = [];
    renderFileList();
    fileName.value = '';
    showStatus('', '');
    showProgress(false);
}

function showStatus(message, type) {
    if (!message) {
        status.innerHTML = '';
        status.className = 'status';
        return;
    }
    status.innerHTML = message;
    status.className = 'status ' + (type || '');
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') clearFiles();
    if (e.ctrlKey && e.key === 'Enter') processBtn.click();
});

console.log('PDFForge loaded! Drop your files to convert.');