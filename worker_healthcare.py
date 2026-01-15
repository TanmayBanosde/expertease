import os
from config import HEALTHCARE_UPLOAD_DIR, HEALTHCARE_REQUIRED_DOCS

def save_healthcare_documents(email, files):
    worker_dir = os.path.join(HEALTHCARE_UPLOAD_DIR, email)
    os.makedirs(worker_dir, exist_ok=True)

    for doc in HEALTHCARE_REQUIRED_DOCS:
        if doc not in files:
            return False, f"{doc} missing"

        file = files[doc]
        file.save(os.path.join(worker_dir, f"{doc}.pdf"))

    return True, "Documents uploaded successfully"
