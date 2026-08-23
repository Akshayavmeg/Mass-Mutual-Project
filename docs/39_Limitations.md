# Limitations

# Limitations

## 1. Introduction

The **AI-Powered Cheque Scanning, Validation & Fraud Detection System** is designed to automate cheque digitization, validation, fraud analysis, and decision support. However, as an MVP/prototype, the system has certain technical, data, operational, and deployment limitations.

These limitations must be considered when evaluating the system. The project should **not claim capabilities that have not been implemented or validated through testing**.

---

## 2. Dependence on Cheque Image Quality

The accuracy of the system depends significantly on the quality of the uploaded cheque image.

The system may have difficulty processing cheques that are:

* Blurred
* Low-resolution
* Rotated significantly
* Cropped
* Overexposed or underexposed
* Torn or damaged
* Partially covered
* Heavily stained
* Poorly scanned

Poor image quality can affect both OCR and fraud-detection performance.

**Mitigation:** Image-quality checks and preprocessing are applied before OCR. Cheques that cannot be reliably processed can be sent for manual review.

---

## 3. OCR Accuracy Limitations

OCR is not guaranteed to extract every cheque field correctly.

Possible errors include:

* Character substitution
* Missing characters
* Incorrect numbers
* Incorrect dates
* Incorrect amount extraction
* Incorrect payee extraction
* Confusion between similar characters

For example:

```text
Actual:
Account Number = 10050826

OCR:
Account Number = 10050828
```

Even a single character error in an important financial field can affect subsequent validation.

Therefore, the **95% OCR accuracy specified in the project requirements is a target and must be demonstrated through evaluation; it should not be assumed to be achieved.**

---

## 4. Handwriting Recognition Limitation

Handwritten cheque fields can be significantly more difficult to recognize than printed text.

The system may have reduced accuracy when dealing with:

* Different handwriting styles
* Very small handwriting
* Overlapping characters
* Poor handwriting
* Cursive writing
* Ink smudging

Additional handwriting-specific OCR or AI models may be required for production-level performance.

---

## 5. Limited Cheque Format Support

Different banks and countries may use different cheque layouts.

Differences may include:

* Field positions
* Account-number formats
* Routing/transit-number formats
* Fonts
* Security features
* MICR formats
* Signature placement

The initial system may therefore be optimized for the **sample cheque formats used during development and testing**.

Supporting a large number of bank-specific cheque layouts would require additional templates, training data, and validation rules.

---

## 6. Mock Banking Data Limitation

The project scope allows the use of **mock banking data** for validation.

Therefore, the MVP cannot demonstrate complete real-world integration with actual banking infrastructure.

The system may simulate:

```text
Account Status
Cheque History
Cheque Number
Payee
Transaction History
Account Details
```

using synthetic records.

These records do not represent real banking customers or real banking transactions.

---

## 7. No Real-Time Core Banking Integration

The current system does not replace or directly integrate with a bank's core banking system.

Therefore, it does not provide:

* Real-time account authorization
* Real-time settlement
* Real-time balance deduction
* Actual cheque clearing
* Direct transaction posting

Such capabilities would require secure integration with authorized banking systems.

---

## 8. Fraud Detection Limitations

Fraud detection is inherently difficult because fraudulent techniques can change over time.

The system may fail to detect:

* Previously unseen fraud patterns
* Highly sophisticated image manipulation
* New forgery techniques
* Fraud that resembles legitimate transaction behavior

Similarly, legitimate cheques may sometimes be flagged as suspicious.

Therefore, the **90% fraud detection accuracy specified in the requirements is a target that must be established through evaluation using an appropriate test dataset.**

---

## 9. False Positives and False Negatives

The system may produce:

### False Positive

A legitimate cheque is incorrectly flagged as suspicious.

```text
Legitimate Cheque
       ↓
Fraud Detector
       ↓
Incorrectly Flagged
```

### False Negative

A fraudulent cheque is incorrectly classified as legitimate.

```text
Fraudulent Cheque
       ↓
Fraud Detector
       ↓
Incorrectly Approved
```

False negatives are particularly important because they can result in fraudulent transactions being missed.

The system therefore includes a **Manual Review** category for uncertain cases.

---

## 10. Signature Analysis Limitation

Signature analysis may not always accurately distinguish genuine and forged signatures.

Performance can be affected by:

* Different signing styles
* Natural variations in a person's signature
* Low-quality signature images
* Signature size differences
* Image distortion
* Lack of a suitable reference signature

The signature result should therefore be treated as **one fraud indicator**, rather than the sole basis for accepting or rejecting a cheque.

---

## 11. Duplicate Detection Limitations

Duplicate detection depends on the availability and quality of historical cheque records.

A duplicate may be difficult to identify if:

* The cheque number is incorrectly extracted.
* The account number is incorrect.
* The cheque image is substantially modified.
* Historical records are incomplete.
* The same cheque appears in a different image format.

Using multiple attributes such as cheque number, account number, amount, date, payee, and image fingerprint can improve duplicate detection, but cannot guarantee detection of every duplicate.

---

## 12. Tampering Detection Limitations

Image-based tampering detection cannot guarantee detection of every manipulation.

Advanced alterations may be difficult to identify, particularly when:

* The modified image has been carefully reconstructed.
* The original cheque image is unavailable for comparison.
* Image quality is poor.
* Manipulated content visually resembles the original.
* Metadata has been removed.

Therefore, tampering detection should be considered a **risk indicator**, not an absolute proof of fraud.

---

## 13. Risk Scoring Limitations

The risk score is based on the fraud indicators and validation results available to the system.

For example:

```text
Signature mismatch       → Risk contribution
Duplicate detected       → Risk contribution
Amount anomaly           → Risk contribution
Account issue            → Risk contribution
Tampering indicator      → Risk contribution
```

The resulting score depends on the quality of the underlying checks.

Incorrect weights or thresholds can lead to inappropriate risk classifications.

Risk thresholds must therefore be evaluated and tuned using representative test data.

---

## 14. Limited Historical Data

The effectiveness of anomaly detection depends on historical transaction data.

The MVP may contain only a limited amount of synthetic historical data.

As a result, the system may have limited ability to identify complex patterns such as:

* Long-term account behavior
* Seasonal transaction patterns
* Unusual customer behavior
* Bank-wide fraud patterns
* Cross-account relationships

A production system would require significantly larger and properly governed datasets.

---

## 15. Dataset Limitations

The quality of AI/ML evaluation depends heavily on the quality and diversity of the dataset.

A limited dataset may not represent:

* Different cheque layouts
* Different handwriting styles
* Different image qualities
* Different fraud techniques
* Different transaction amounts
* Different account behaviors

Therefore, test results obtained from a small prototype dataset should not automatically be generalized to all real-world cheques.

---

## 16. No Guarantee of Automated Decision Accuracy

The system generates one of three decisions:

```text
APPROVE
REVIEW
REJECT
```

However, automated decisions are dependent on:

* OCR accuracy
* Validation results
* Fraud detection
* Signature analysis
* Duplicate detection
* Anomaly detection
* Risk thresholds

An incorrect upstream result can affect the final decision.

Therefore, the system should be considered a **decision-support and automated processing system**, not an infallible fraud authority.

---

## 17. Manual Review Still Required

Although the project aims to reduce manual verification effort, manual review cannot be completely eliminated.

Cases requiring review may include:

* Low-quality images
* Low OCR confidence
* Conflicting validation results
* Suspicious signatures
* Possible tampering
* Duplicate indicators
* High-risk transactions
* Incomplete information

The system is intended to **reduce unnecessary manual verification**, not eliminate human oversight entirely.

---

## 18. Processing-Time Limitation

The project specifies a target of:

> **Less than 30 seconds per cheque.**

Actual processing time may vary depending on:

* Image size
* OCR processing time
* AI/ML model execution
* Database response time
* Hardware resources
* Number of fraud checks
* Network latency when external services are used

Therefore, the <30-second requirement must be verified through actual performance testing.

---

## 19. Limited File Format Scope

The system is designed to support:

* JPEG
* PNG
* PDF

Other formats may not be supported without additional implementation.

Unsupported or corrupted files should be rejected during the input-validation stage.

---

## 20. Security and Privacy Limitations

The system processes sensitive financial-document information.

Although security controls can be implemented, an MVP should not be considered equivalent to a fully audited enterprise banking platform.

Additional controls may be required for production, including:

* Enterprise identity management
* Advanced encryption and key management
* Security monitoring
* Penetration testing
* Vulnerability management
* Compliance audits
* Data-loss prevention
* Enterprise access governance

---

## 21. Regulatory and Compliance Limitation

The prototype does not automatically establish compliance with banking or financial regulations.

Actual production deployment would require review against applicable:

* Banking regulations
* Data-protection requirements
* Organizational security policies
* Financial-record requirements
* Audit requirements
* Data-retention policies

Compliance must be validated by the appropriate organization and regulatory authorities.

---

## 22. Cloud Dependency Limitation

If cloud-based services such as cloud OCR, object storage, or AI services are used, the system may depend on:

* Internet connectivity
* Cloud service availability
* API limits
* Service pricing
* Cloud configuration
* Network latency

For the MVP, local processing can be used where practical to reduce external dependencies.

---

## 23. Model Explainability Limitation

Some AI/ML models may not provide a complete explanation for every prediction.

For example, a fraud model may generate:

```text
Fraud Risk Score = 82
```

but the score itself is not sufficient as an explanation.

The system should therefore complement model predictions with understandable indicators such as:

```text
✓ Account valid
✓ Cheque number valid
✗ Signature similarity low
✗ Duplicate indicator detected
✓ Date valid
```

This improves transparency for manual reviewers.

---

## 24. Scalability Limitation

The MVP architecture is primarily designed for development, demonstration, and controlled testing.

It may not initially support very large transaction volumes.

Enterprise deployment would require additional infrastructure such as:

* Load balancing
* Multiple backend instances
* Queue-based processing
* Independent OCR services
* Independent fraud-detection services
* Database scaling
* Distributed storage
* Monitoring infrastructure

---

## 25. Lack of Real Production Fraud Dataset

Real fraudulent cheque datasets are difficult to obtain because they contain highly sensitive financial information.

Therefore, the project may rely primarily on:

* Synthetic banking records
* Sample cheque images
* Artificially modified cheque images
* Controlled test cases

This limits the ability to fully validate real-world fraud detection performance.

---

## 26. Dependency on Reference Signatures

Signature comparison requires an appropriate reference signature or equivalent authorized data.

If no reliable reference is available, signature verification may not be possible.

In such cases:

```text
No Reference Signature
        ↓
Cannot Reliably Compare
        ↓
Manual Review
```

---

## 27. Limited Internationalization

The initial implementation may focus on a particular cheque format, currency, date format, and banking identifier structure.

Supporting international cheque formats would require additional:

* OCR configurations
* Currency handling
* Date formats
* Routing-number formats
* Bank-specific rules
* Cheque templates

---

## 28. Limitations of the MVP

The initial MVP focuses on demonstrating the complete processing pipeline:

```text
Upload
  ↓
Preprocessing
  ↓
OCR
  ↓
Extraction
  ↓
Validation
  ↓
Fraud Detection
  ↓
Risk Scoring
  ↓
Decision
  ↓
Audit Trail
```

It does not attempt to implement every capability required by a production banking platform.

---

# 29. Summary of Major Limitations

| Limitation                  | Effect                                                          |
| --------------------------- | --------------------------------------------------------------- |
| Image quality dependency    | Can reduce OCR and fraud-analysis accuracy                      |
| OCR errors                  | Can cause incorrect field extraction                            |
| Limited cheque formats      | May not support all banks/layouts                               |
| Mock banking data           | Does not represent live banking infrastructure                  |
| No core banking integration | No real-time settlement or transaction posting                  |
| Limited fraud dataset       | May reduce generalization of fraud detection                    |
| False positives             | Legitimate cheques may require manual review                    |
| False negatives             | Some fraudulent cheques may not be detected                     |
| Signature limitations       | Cannot guarantee forgery detection                              |
| Tampering limitations       | Sophisticated manipulation may remain undetected                |
| Limited historical data     | Reduces anomaly-detection capability                            |
| Processing variability      | <30-second target requires actual testing                       |
| Manual review               | Human intervention remains necessary for uncertain cases        |
| Security scope              | MVP is not equivalent to a production banking security platform |
| Compliance                  | Regulatory compliance requires separate assessment              |
| Scalability                 | Enterprise-scale workloads require additional infrastructure    |

---

# 30. Conclusion

The **AI-Powered Cheque Scanning, Validation & Fraud Detection System** can significantly automate cheque processing and reduce manual verification effort, but it has important limitations.

The most significant limitations are **OCR errors, image-quality dependency, limited training/test data, mock banking integration, evolving fraud patterns, signature-analysis uncertainty, and the possibility of false positives and false negatives**.

The system should therefore use **manual review for uncertain or high-risk cases** rather than assuming that automated analysis is always correct.

The limitations documented here define the boundaries of the proposed MVP and provide a clear foundation for the **Future Roadmap**, where additional datasets, advanced AI models, real banking integrations, stronger security controls, broader cheque-format support, and enterprise-scale infrastructure can be introduced.

