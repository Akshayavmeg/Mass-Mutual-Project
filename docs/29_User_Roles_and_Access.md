# User Roles and Access

# 29. User Roles and Access

## 1. Introduction

The **User Roles and Access** module defines who can access the Mass-Mutual cheque processing system and what actions each user is authorized to perform.

Since the system handles sensitive cheque and banking information, users must not have unrestricted access to every feature. The system follows a **Role-Based Access Control (RBAC)** approach, where permissions are assigned to roles rather than individually to every user.

The main principle is:

> **Users should receive only the permissions required to perform their responsibilities.**

---

# 2. Objectives

The User Roles and Access module aims to:

1. Control access to system functionality.
2. Prevent unauthorized access to sensitive cheque information.
3. Separate operational, review, administrative, and auditing responsibilities.
4. Implement Role-Based Access Control (RBAC).
5. Restrict approval and rejection privileges to authorized users.
6. Protect fraud-analysis information.
7. Restrict access to audit records.
8. Maintain accountability for user actions.
9. Follow the principle of least privilege.
10. Prevent privilege escalation.

---

# 3. Roles in the System

The proposed system contains the following primary roles:

| Role               | Main Responsibility                                                         |
| ------------------ | --------------------------------------------------------------------------- |
| **Administrator**  | Manage users, roles, system configuration, and overall administration       |
| **Operator**       | Upload cheques and monitor automated processing                             |
| **Reviewer**       | Investigate flagged cheques and perform manual review                       |
| **Auditor**        | View audit history, reports, and system activities                          |
| **System Service** | Perform automated OCR, validation, fraud detection, and decision processing |

---

# 4. Role Hierarchy

The logical access structure is:

```text
                    ADMINISTRATOR
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
          OPERATOR     REVIEWER     AUDITOR
              │           │           │
              └───────────┼───────────┘
                          │
                          ▼
                    SYSTEM SERVICE
```

The **System Service** is not a normal human user. It represents trusted backend services that perform automated processing.

---

# 5. Administrator

## Responsibility

The Administrator is responsible for managing the overall application environment.

### Permissions

The Administrator can:

* Create users.
* Disable users.
* Assign roles.
* Modify user permissions.
* View system configuration.
* View system-level dashboards.
* View audit logs.
* Manage application settings.
* Monitor system health.
* Manage fraud-model configuration where authorized.
* View processing statistics.

### Restrictions

The Administrator should not automatically be able to modify historical audit records.

Audit records should remain **append-only**, even for administrators.

---

# 6. Operator

## Responsibility

The Operator handles the initial cheque-processing workflow.

### Permissions

The Operator can:

* Log into the system.
* Upload cheque images.
* Upload supported PDF files.
* View uploaded cheques.
* Start cheque processing.
* View OCR results.
* View validation results.
* View processing status.
* View system-generated decisions where permitted.
* Search cheque records.

### Restrictions

The Operator cannot:

* Modify system configuration.
* Manage users.
* Change fraud-model settings.
* Delete audit records.
* Modify historical processing results.
* Override a high-risk decision unless explicitly authorized by the workflow.

---

# 7. Reviewer

## Responsibility

The Reviewer handles cheques that are flagged for **manual review**.

A cheque may be sent to a reviewer because of:

* Signature mismatch.
* Duplicate detection.
* Unusual amount.
* Account-status issue.
* Payee mismatch.
* Suspicious image modification.
* High fraud score.
* Other validation failures.

### Permissions

The Reviewer can:

* View assigned review cases.
* View cheque images.
* View extracted cheque data.
* View validation results.
* View fraud indicators.
* View risk score.
* Compare cheque information with available mock banking records.
* Add review comments.
* Request additional investigation.
* Approve a cheque after manual verification.
* Reject a cheque after manual verification.
* Escalate a suspicious case.

### Restrictions

The Reviewer cannot:

* Create or delete users.
* Change application configuration.
* Modify fraud-model parameters.
* Modify historical audit records.
* Access unrelated administrative functions.

---

# 8. Auditor

## Responsibility

The Auditor is responsible for examining system activity and processing history.

### Permissions

The Auditor can:

* View audit logs.
* Search audit records.
* View cheque processing history.
* View decision history.
* View manual review actions.
* View system activity.
* Generate audit reports.
* Review fraud-related events.
* Review user activity.

### Restrictions

The Auditor should normally have **read-only access**.

The Auditor cannot:

* Upload cheques.
* Approve cheques.
* Reject cheques.
* Modify audit records.
* Modify user permissions.
* Change system configuration.

---

# 9. System Service

The System Service represents automated backend components.

It performs tasks such as:

```text
OCR
 ↓
Data Extraction
 ↓
Validation
 ↓
Fraud Detection
 ↓
Signature Analysis
 ↓
Duplicate Detection
 ↓
Anomaly Detection
 ↓
Risk Scoring
 ↓
Decision Generation
```

### Permissions

The System Service can:

* Read uploaded cheque images.
* Store OCR results.
* Read mock banking records required for validation.
* Execute validation rules.
* Execute fraud detection.
* Generate risk scores.
* Generate automated decisions.
* Create audit events.
* Update processing status.

### Restrictions

The System Service should not:

* Manage human users.
* Change user roles.
* Modify its own permissions.
* Delete audit records.
* Perform actions outside its assigned service permissions.

---

# 10. Permission Matrix

The following matrix defines the proposed access control.

| Function                   |       Admin      | Operator |    Reviewer    | Auditor |   System   |
| -------------------------- | :--------------: | :------: | :------------: | :-----: | :--------: |
| Login                      |         ✓        |     ✓    |        ✓       |    ✓    |      ✓     |
| Upload Cheque              |         ✓        |     ✓    |        ✗       |    ✗    |      ✗     |
| View Cheque                |         ✓        |     ✓    |        ✓       |    ✓    |      ✓     |
| Start Processing           |         ✓        |     ✓    |        ✗       |    ✗    |      ✓     |
| View OCR Results           |         ✓        |     ✓    |        ✓       |    ✓    |      ✓     |
| View Validation Results    |         ✓        |     ✓    |        ✓       |    ✓    |      ✓     |
| View Fraud Results         |         ✓        |  Limited |        ✓       |    ✓    |      ✓     |
| View Risk Score            |         ✓        |  Limited |        ✓       |    ✓    |      ✓     |
| Create Review Case         |         ✓        |     ✓    |        ✓       |    ✗    |      ✓     |
| Perform Manual Review      |        ✗*        |     ✗    |        ✓       |    ✗    |      ✗     |
| Approve Cheque             |    Controlled    |     ✗    |        ✓       |    ✗    |     ✓**    |
| Reject Cheque              |    Controlled    |     ✗    |        ✓       |    ✗    |     ✓**    |
| Add Review Comments        |         ✓        |     ✗    |        ✓       |    ✗    |      ✗     |
| View Audit Trail           |         ✓        |  Limited | Assigned Cases |    ✓    |      ✓     |
| Generate Reports           |         ✓        |  Limited |        ✓       |    ✓    |      ✓     |
| Manage Users               |         ✓        |     ✗    |        ✗       |    ✗    |      ✗     |
| Manage Roles               |         ✓        |     ✗    |        ✗       |    ✗    |      ✗     |
| System Configuration       |         ✓        |     ✗    |        ✗       |    ✗    |      ✗     |
| Modify Fraud Configuration | Authorized Admin |     ✗    |        ✗       |    ✗    | Controlled |
| Delete Audit Records       |         ✗        |     ✗    |        ✗       |    ✗    |      ✗     |

* Administrator access to manual review should be controlled according to organizational policy.

** The System Service can generate **automated** approval/rejection decisions according to configured rules; human approval requirements can be enforced for selected risk levels.

---

# 11. Access Levels

The system uses different levels of access.

### Level 1 — Basic Access

Users can:

* Log in.
* View their permitted dashboard.
* View permitted system information.

### Level 2 — Operational Access

Operators can:

* Upload cheques.
* Process cheques.
* View processing results.

### Level 3 — Review Access

Reviewers can:

* Investigate flagged cheques.
* View detailed fraud indicators.
* Make authorized manual decisions.

### Level 4 — Audit Access

Auditors can:

* Access historical audit information.
* Generate compliance and activity reports.

### Level 5 — Administrative Access

Administrators can:

* Manage users.
* Manage roles.
* Configure the system.

---

# 12. Least Privilege Principle

The system follows the **principle of least privilege**.

For example:

An Operator needs to upload a cheque.

Therefore:

```text
Operator
   ↓
Upload Permission ✓
```

But the Operator does not need:

```text
Manage Users ✗
Modify System Configuration ✗
Delete Audit Logs ✗
```

Similarly, an Auditor needs to examine records but does not need to approve cheques.

---

# 13. Separation of Duties

Important responsibilities should be separated between different roles.

For example:

```text
Operator
   ↓
Uploads Cheque
   ↓
System Processing
   ↓
High Risk
   ↓
Reviewer
   ↓
Manual Investigation
   ↓
Final Decision
```

This prevents a single user from controlling the entire process.

---

# 14. Manual Review Access

Only authorized Reviewers should be able to perform manual review.

Example:

```text
Automated Decision
       │
       ├── APPROVE → Completed
       │
       ├── REJECT → Completed
       │
       └── REVIEW
             ↓
       Reviewer Queue
             ↓
       Authorized Reviewer
             ↓
       Investigation
             ↓
       APPROVE / REJECT / ESCALATE
```

Every manual decision must be recorded in the audit trail.

---

# 15. Access to Sensitive Data

Not every role should see every piece of cheque information.

Example:

| Data             | Admin | Operator |  Reviewer  |   Auditor  |
| ---------------- | :---: | :------: | :--------: | :--------: |
| Cheque Image     |   ✓   |     ✓    |      ✓     | Controlled |
| Cheque Number    |   ✓   |     ✓    |      ✓     |      ✓     |
| Account Number   |   ✓   |  Masked  | Authorized |   Masked   |
| Payee            |   ✓   |     ✓    |      ✓     |      ✓     |
| Amount           |   ✓   |     ✓    |      ✓     |      ✓     |
| Signature Image  |   ✓   |  Limited |      ✓     | Controlled |
| Fraud Indicators |   ✓   |  Limited |      ✓     |      ✓     |
| Risk Score       |   ✓   |  Limited |      ✓     |      ✓     |
| Audit History    |   ✓   |  Limited |  Assigned  |      ✓     |

Sensitive information should be displayed according to the user's permissions.

---

# 16. User Authentication Flow

The login process is:

```text
User
  ↓
Enter Username & Password
  ↓
Authentication
  ↓
Credentials Valid?
  │
  ├── NO → Access Denied → Audit Event
  │
  └── YES
       ↓
   Identify Role
       ↓
   Create Session/Token
       ↓
   Open Authorized Dashboard
```

---

# 17. Authorization Flow

For every protected operation:

```text
User Request
      ↓
Authenticated?
      │
      ├── NO → 401 Unauthorized
      │
      ▼
Identify User Role
      ↓
Check Permission
      │
      ├── NO → 403 Forbidden
      │
      ▼
Perform Operation
      ↓
Create Audit Event
```

This ensures that authentication and authorization are checked before sensitive operations.

---

# 18. Unauthorized Access

If a user attempts to perform an action outside their permissions:

```text
Operator
    ↓
Attempt: Manage Users
    ↓
Permission Check
    ↓
DENIED
    ↓
403 Forbidden
    ↓
ACCESS_DENIED audit event
```

The system should not expose unnecessary information about restricted resources.

---

# 19. User Account Management

The Administrator can manage user accounts.

Supported operations include:

```text
Create User
    ↓
Assign Role
    ↓
Activate Account
    ↓
User Login
    ↓
Account Monitoring
    ↓
Disable Account
```

When a user leaves the project or no longer requires access, their account should be disabled rather than simply ignored.

---

# 20. Account Status

Each user account can have a status:

```text
ACTIVE
INACTIVE
SUSPENDED
DISABLED
```

Example:

| Status    | Access              |
| --------- | ------------------- |
| ACTIVE    | Allowed             |
| INACTIVE  | Not allowed         |
| SUSPENDED | Temporarily blocked |
| DISABLED  | Not allowed         |

---

# 21. Auditability of User Actions

Important user actions must generate audit events.

Examples:

```text
USER_LOGIN
USER_LOGOUT
CHEQUE_UPLOADED
CHEQUE_VIEWED
REVIEW_STARTED
REVIEW_UPDATED
DECISION_GENERATED
MANUAL_DECISION_MADE
ACCESS_DENIED
```

Example:

```text
Reviewer USR-007
       ↓
Opened CHK-2026-000087
       ↓
Added review comment
       ↓
Changed decision to REJECT
       ↓
Audit event created
```

This provides accountability.

---

# 22. Privilege Escalation Protection

Users must not be able to change their own roles or permissions.

For example:

```text
Operator
   ↓
Attempts to change role
   ↓
Operator → Administrator
   ↓
Permission Check
   ↓
DENIED
```

Only authorized administrators should be able to assign roles.

---

# 23. Role Assignment

A role assignment can be represented as:

```text
User
 │
 └── Role
       │
       ├── Permissions
       ├── Dashboard Access
       └── Data Access
```

Example:

```text
USR-001
   ↓
OPERATOR
   ↓
UPLOAD_CHEQUE
VIEW_CHEQUE
VIEW_PROCESSING_STATUS
```

---

# 24. Role-Based Dashboard

Each role should receive an appropriate dashboard.

### Operator Dashboard

```text
┌───────────────────────────────┐
│ Operator Dashboard            │
├───────────────────────────────┤
│ Upload Cheque                 │
│ Recent Cheques                │
│ Processing Status             │
│ OCR Results                   │
│ Validation Results            │
└───────────────────────────────┘
```

### Reviewer Dashboard

```text
┌───────────────────────────────┐
│ Reviewer Dashboard            │
├───────────────────────────────┤
│ Pending Reviews               │
│ High Risk Cheques             │
│ Fraud Indicators              │
│ Risk Scores                   │
│ Review History                │
└───────────────────────────────┘
```

### Auditor Dashboard

```text
┌───────────────────────────────┐
│ Auditor Dashboard             │
├───────────────────────────────┤
│ Audit Logs                    │
│ User Activity                 │
│ Decision History              │
│ Fraud Events                  │
│ Reports                       │
└───────────────────────────────┘
```

### Administrator Dashboard

```text
┌───────────────────────────────┐
│ Administrator Dashboard       │
├───────────────────────────────┤
│ User Management               │
│ System Configuration          │
│ System Health                 │
│ Processing Statistics         │
│ Audit Logs                    │
└───────────────────────────────┘
```

---

# 25. Access Control for the API

The backend should enforce permissions at the API level, not only through the frontend.

For example:

```text
Frontend hides "Approve" button
        ≠
Backend security
```

A malicious user could still manually send an API request.

Therefore:

```text
Frontend Permission Check
          +
Backend Permission Check
          ↓
      Secure Access
```

The backend must always perform the final authorization check.

---

# 26. Example Permission Definitions

The system can define permissions such as:

```text
CHEQUE_UPLOAD
CHEQUE_VIEW
CHEQUE_PROCESS
OCR_VIEW
VALIDATION_VIEW
FRAUD_VIEW
RISK_VIEW
REVIEW_VIEW
REVIEW_UPDATE
DECISION_APPROVE
DECISION_REJECT
AUDIT_VIEW
REPORT_VIEW
USER_MANAGE
ROLE_MANAGE
SYSTEM_CONFIG
```

Roles are then mapped to these permissions.

---

# 27. Example RBAC Configuration

Conceptually:

```json
{
  "roles": {
    "OPERATOR": [
      "CHEQUE_UPLOAD",
      "CHEQUE_VIEW",
      "CHEQUE_PROCESS",
      "OCR_VIEW",
      "VALIDATION_VIEW"
    ],
    "REVIEWER": [
      "CHEQUE_VIEW",
      "OCR_VIEW",
      "VALIDATION_VIEW",
      "FRAUD_VIEW",
      "RISK_VIEW",
      "REVIEW_VIEW",
      "REVIEW_UPDATE",
      "DECISION_APPROVE",
      "DECISION_REJECT"
    ],
    "AUDITOR": [
      "CHEQUE_VIEW",
      "AUDIT_VIEW",
      "REPORT_VIEW"
    ],
    "ADMINISTRATOR": [
      "CHEQUE_VIEW",
      "AUDIT_VIEW",
      "REPORT_VIEW",
      "USER_MANAGE",
      "ROLE_MANAGE",
      "SYSTEM_CONFIG"
    ]
  }
}
```

The exact implementation can be adapted to the selected backend framework.

---

# 28. Access-Control Success Criteria

The User Roles and Access module will be considered successfully implemented when:

* Every user has an assigned role.
* Users cannot access functions outside their permissions.
* Operators can perform operational cheque-processing tasks.
* Reviewers can investigate flagged cheques.
* Auditors have read-only audit access.
* Administrators can manage users and system configuration.
* Automated services have controlled system permissions.
* Sensitive information is restricted according to role.
* Manual decisions are limited to authorized users.
* Unauthorized access attempts are rejected and logged.
* Users cannot change their own roles.
* Backend APIs enforce authorization independently of the frontend.
* Important user actions are recorded in the audit trail.

---

# 29. Summary

The **User Roles and Access** module provides controlled access to the Mass-Mutual cheque processing platform through **Role-Based Access Control (RBAC)**.

The system separates responsibilities among **Administrator, Operator, Reviewer, Auditor, and System Service** roles. Each role receives only the permissions necessary to perform its assigned responsibilities.

This separation protects sensitive cheque information, prevents unauthorized operations, supports **least privilege and separation of duties**, and ensures that important actions such as manual approvals, rejections, and administrative changes remain traceable through the Audit Trail.

