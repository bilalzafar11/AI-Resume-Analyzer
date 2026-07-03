// File upload validation
document.addEventListener('DOMContentLoaded', function() {
  const fileInput = document.getElementById('cv-file');
  
  if (fileInput) {
    fileInput.addEventListener('change', function() {
      const file = this.files[0];
      if (file) {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const fileName = file.name.toLowerCase();
        
        if (!validTypes.includes(file.type) && !fileName.endsWith('.docx') && !fileName.endsWith('.pdf')) {
          alert('Please upload a valid PDF or DOCX file');
          this.value = '';
        }
      }
    });
  }
});

// Form submission handler
const uploadForm = document.querySelector('.form-modern');
if (uploadForm) {
  uploadForm.addEventListener('submit', function(e) {
    const fileInput = document.getElementById('cv-file');
    const jobDesc = document.getElementById('job-desc');
    
    if (!fileInput.files.length) {
      e.preventDefault();
      alert('Please select a resume file');
      return false;
    }
    
    if (!jobDesc.value.trim()) {
      e.preventDefault();
      alert('Please enter job description keywords');
      return false;
    }
  });
}
  