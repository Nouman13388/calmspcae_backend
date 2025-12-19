# 🌿 CalmSpace Backend – Simple Explanation

This guide explains how CalmSpace handles **user accounts**, **logging in**, **email verification**, **password resets**, and **permissions** (who can access what).

Think of it as the “rules” and “systems” behind the scenes that keep the app safe and organized.

---

# ✅ 1. Setting Things Up

Before the system can run:

* Email settings must be added so the app can **send verification and password reset emails**.
* Necessary packages are installed.
* The database is prepared.
* User roles (Admin, Staff, Customer, Therapist) are created.
* An admin account is created.

---

# 👤 2. Custom User Accounts

CalmSpace doesn’t use the default Django user model. Instead, it has a upgraded version that stores:

* Email
* Name
* Phone number
* Profile picture
* User type (Customer, Staff, Admin, Therapist)
* Email verification status
* When the account was created

**Email is the main way users log in.**

---

# 🔐 3. Authentication (Login System)

These are the main features for users signing up and logging in:

### **Register (Create an account)**

User signs up, enters their details, and receives an email to verify their account.

### **Login**

User enters email + password → receives an “access token” (like a digital key) to stay logged in.

### **Logout**

User logs out and their token becomes invalid.

---

# ✉️ 4. Email Verification

After registering, users must confirm their email.

The flow:

1. User gets an email with a link.
2. Click link → account becomes “verified.”
3. If needed, user can request a new link.

This increases security and ensures the email is real.

---

# 🔑 5. Password Reset

If a user forgets their password:

1. They enter their email.
2. They receive a reset link.
3. They set a new password.

This ensures users can recover their account safely.

---

# 🔒 6. Role-Based Access Control (Who can access what)

CalmSpace has 4 user roles:

* **Customer** – regular users
* **Staff** – internal team
* **Admin** – full control over the system
* **Therapist** – mental health professionals

Certain features/pages are restricted based on these roles.
For example:

* Only **Admins** can access admin dashboards.
* Only **Therapists** can see therapist tools.

This keeps the system organized and secure.

---

# 🧑‍💼 7. Profile Management

Users can:

* View their profile
* Update their info (name, phone, picture)
* Change password

All actions require being logged in.

---

# 🛡️ 8. Permissions & Decorators

These are simply “rules” added to parts of the backend that say:

* “Only Admins can access this.”
* “Only Verified users can enter here.”
* “Only the owner of the profile can edit it.”

This ensures data is protected and only accessible to the right people.

---

# 🧪 9. Testing & Troubleshooting

The document provides tips for:

* Email problems
* Token expiration
* Login issues
* Image upload problems

This helps developers fix issues quickly.

---

# ⭐ Best Practices

To keep the system secure:

* Use HTTPS
* Use strong passwords
* Verify emails
* Backup the database
* Limit how many attempts users can make to log in

---

# Summary (One Sentence)

**CalmSpace’s backend provides a secure system for user accounts, email confirmation, password recovery, and access control based on different user roles.**
