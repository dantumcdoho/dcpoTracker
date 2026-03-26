# 🏛️ CHD-CAR DCPO Tracker System

An official Personnel Order (DCPO) Management and Public Tracking System developed for the **Department of Health - Center for Health Development - Cordillera (CHD-CAR)**. 

This application provides a centralized, cloud-based platform to track, manage, and view Regional Personnel Orders with integrated digital soft copies.

---

## ✨ Key Features

* **🔐 Secure Admin Portal:** Full CRUD (Create, Read, Update, Delete) capabilities for authorized users with automated sequence numbering (e.g., `2024-001`).
* **📖 Public Guest View:** A streamlined, searchable dashboard for staff to verify Personnel Orders without requiring an account.
* **📂 Digital Document Integration:** Direct access to soft copies (Google Drive/SharePoint) via clickable link columns directly in the data table.
* **🔍 Advanced Filtering:** Instant search across all fields (Order Number, Organization, Venue, Status).
* **⛰️ Cordillera Branding:** Custom UI implementation using the official **Forest Green (#006400)** and **Mountain Gold (#FFD700)** palette.

---

## 🛠️ Technology Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python Framework)
* **Database:** [Google Sheets](https://sheets.google.com/) via `streamlit-gsheets`
* **Styling:** Custom CSS Injection & Streamlit Themes

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/cpdoho_dcpo_tracker_online.git](https://github.com/your-username/cpdoho_dcpo_tracker_online.git)
cd cpdoho_dcpo_tracker_online