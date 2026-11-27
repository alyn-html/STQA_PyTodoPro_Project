# STQA_PyTodoPro_Project
---

**Course:** Software Testing and Quality Assurance (STQA)  
**Course Code:** TEB3433 / TFB3433  
**Semester:** September 2026  
**Project:** PyTodo Pro – Software Quality Evaluation 

## Team Members

**Group Number:** 6 
| No. | Name | Student ID | Main Responsibility |
|---|---|---|---|
| 1 | Alya Nabihah bt Ahmad Kamarzaman | 22012109 | Web/API, Security & Performance Testing |
| 2 | Wan Danihaziq bin Wan Adrie | 22005555  | White-Box Testing, Automation, GUI & Usability |
| 3 | Mohammad Haiqal Firdaus Bin Mad Husni | 22006428  | Test Planning, Black-Box Testing & Test Management |

## 1. Project Overview

This repository contains the documentation, test cases, test scripts, test results and quality evaluation produced for the **Software Testing and Quality Assurance (STQA) Group Project**.

The project focuses on conducting a systematic and evidence-based quality assessment of **PyTodo Pro**, an existing task-management web application developed using Flask and Python.

Rather than developing or modifying the application, our group acts as an independent Software Quality Assurance (SQA) team. We apply software testing techniques and quality assurance principles to evaluate the application's functionality, reliability, security, usability and performance.

Testing activities are conducted progressively throughout the semester, with findings documented and analysed to form an overall assessment of the application's software quality.

## 2. Project Objectives

The main objective is to evaluate the quality of PyTodo Pro through the practical application of software testing and quality assurance techniques.

The specific objectives are to:

- Understand the application's features, users, requirements and expected behaviour.
- Identify testable requirements, quality attributes and potential software risks.
- Develop a structured test plan and Requirements Traceability Matrix (RTM).
- Design and execute black-box and white-box test cases.
- Apply test automation and evaluate code coverage.
- Conduct GUI, usability and accessibility testing.
- Evaluate REST API functionality and behaviour.
- Perform security and performance testing.
- Identify, classify and document software defects.
- Analyse testing results using appropriate metrics and risk-based evaluation.
- Assess the application's quality using recognised software quality principles and standards.
- Present the overall findings through a consolidated QA report, repository and project presentation.

## 3. Application Under Test

**Application:** PyTodo Pro  
**Application Type:** Web-based task management system  
**Backend Framework:** Flask  
**Programming Language:** Python  
**Database:** SQLite  

PyTodo Pro allows authenticated users to manage personal tasks through a web interface.

The main application features include:

| Feature | Description |
|---|---|
| User Registration | Allows new users to create an account. |
| User Login | Provides authenticated access to the application. |
| Task Management | Allows users to create, view, edit and delete tasks. |
| Task Completion | Allows users to mark tasks as completed or open. |
| Task Filtering | Supports filtering and organising task records. |
| Task Urgency | Displays task urgency based on due dates and completion status. |
| Dashboard | Displays task summaries and activity information. |
| REST API | Provides endpoints for authentication, tasks, categories and dashboard information. |

The application serves as the system under test throughout the investigation.

## 4. Testing Scope

The project covers several complementary testing activities to evaluate different aspects of PyTodo Pro.

| Testing Area | Main Focus |
|---|---|
| Test Planning and Management | Define testing scope, objectives, risks, schedules and traceability. |
| Black-Box Testing | Evaluate application behaviour using external inputs and expected outputs. |
| White-Box Testing | Examine selected internal logic, execution paths and code coverage. |
| Test Automation | Automate selected test cases and support repeatable regression testing. |
| GUI Testing | Evaluate interface behaviour, layout and interactive elements. |
| Usability and Accessibility Testing | Assess ease of use and selected accessibility requirements. |
| API Testing | Evaluate REST API endpoints, requests, responses and validation. |
| Security Testing | Examine authentication, authorisation, input validation and potential vulnerabilities. |
| Performance Testing | Measure response times and request-handling behaviour under controlled workloads. |
| Quality Evaluation | Analyse test metrics, defects, risks and software quality characteristics. |

### Scope Exclusions

The project focuses on evaluating the existing application. Therefore:

- The original application is not developed or redesigned by the QA team.
- Application source code is not modified to implement permanent fixes.
- Testing conclusions are limited to the tested features, environment and conditions.
- Recommendations are documented for potential future improvements rather than presented as completed fixes.

## 5. Team Responsibilities and Task Division

The project activities are organised into three main workstreams. Although each member has primary responsibilities, the overall investigation is a collaborative effort involving documentation, result reviews and integration.

### Member 1 – Test Planning, Black-Box Testing and Test Management

**Main responsibility:** Testing preparation, manual functional testing and test management documentation.

Key activities:

- Analyse the application and identify its functional requirements.
- Prepare the test plan and testing scope.
- Conduct risk assessment and prioritise testing activities.
- Develop black-box test cases using:
  - Equivalence Partitioning (EP)
  - Boundary Value Analysis (BVA)
  - Decision Table Testing
  - State Transition Testing
- Execute manual functional test cases.
- Record actual results and identify defects.
- Prepare the Requirements Traceability Matrix (RTM).
- Maintain the consolidated defect log.
- Summarise test execution results and test management metrics.

### Member 2 – White-Box Testing, Automation, GUI and Usability

**Main responsibility:** Structural testing, automated test execution and interface quality evaluation.

Key activities:

- Design and execute selected white-box test cases.
- Examine internal program logic and control flow.
- Perform code coverage analysis.
- Develop and execute automated test scripts.
- Apply suitable automation tools for functional and regression testing.
- Conduct GUI testing to evaluate interface behaviour.
- Perform usability and accessibility checks.
- Analyse automation results, coverage and identified defects.
- Document automation limitations and opportunities for improvement.

### Member 3 – API, Security and Performance Testing

**Main responsibility:** Evaluating API behaviour, application security and performance.

Key activities:

- Identify and evaluate the available REST API endpoints.
- Design and execute API test cases.
- Validate HTTP methods, status codes, request inputs and response behaviour.
- Conduct security testing covering authentication, session management, authorisation and input validation.
- Apply STRIDE threat modelling to identify potential security threats.
- Perform performance testing using sequential and concurrent requests.
- Measure response time, average response time, median, P95, maximum response time, throughput and error rate.
- Document security and performance findings.
- Analyse identified risks and recommend improvements.

### Shared Responsibilities

All members contribute to:

- Reviewing test results and ensuring consistency.
- Maintaining accurate and reproducible documentation.
- Integrating individual testing activities into the overall QA report.
- Discussing defects and their potential impact.
- Evaluating the application's overall quality.
- Preparing the final presentation and project demonstration.

## 6. Testing Tools and Technologies

The following tools and technologies are used across the investigation.

| Tool / Technology | Purpose |
|---|---|
| Python | Programming language used by the application and testing scripts. |
| Flask | Backend framework of PyTodo Pro. |
| SQLite | Application database. |
| PyTest | Automated test execution and test organisation. |
| Flask Test Client | Testing Flask application routes and responses. |
| Selenium | Browser-based GUI automation. |
| axe-core | Automated accessibility checking. |
| pytest-cov | Measuring code coverage during automated testing. |
| PowerShell | Executing HTTP requests and performance testing scripts. |
| IntelliJ IDEA | Development and testing environment. |
| Web Browser | Manual GUI and usability testing. |
| Git and GitHub | Version control, collaboration and project documentation. |

Tools are selected according to the requirements of each testing activity. Test design and result interpretation remain essential; tools are used to support the investigation rather than replace QA judgement.

## 8. Overall Testing Approach

The investigation follows a progressive testing approach throughout the semester.

1. **Application Analysis:** Understand the application, its features, requirements and expected behaviour.
2. **Test Planning:** Define the scope, objectives, risks, priorities and test conditions.
3. **Test Design:** Develop test cases using suitable black-box and white-box techniques.
4. **Test Execution:** Perform manual, automated, GUI, API, security and performance testing.
5. **Defect Management:** Record and classify defects based on their observed behaviour and impact.
6. **Metrics and Analysis:** Evaluate execution results, code coverage, performance measurements and defect trends.
7. **Quality Evaluation:** Assess the application using relevant software quality characteristics and standards.
8. **Reporting and Presentation:** Consolidate findings, limitations and recommendations into the final QA report and presentation.

This approach ensures that testing activities are connected and that findings from one testing area can inform the overall quality assessment.

## 9. Standards and Quality Frameworks

The project refers to recognised quality principles and standards to support its evaluation.

**ISO/IEC 25010 – Software Product Quality**

Used as a reference model for evaluating software product quality characteristics, including functional suitability, performance efficiency, compatibility, interaction capability, reliability, security, maintainability and flexibility.

**ISO 9001 – Quality Management Principles**

Used as a reference for understanding process-oriented quality management, documentation, responsibilities, evidence-based decisions and continuous improvement.

**STRIDE Threat Modelling**

Applied during security analysis to consider potential threats involving:

- Spoofing
- Tampering
- Repudiation
- Information Disclosure
- Denial of Service
- Elevation of Privilege

These frameworks support the evaluation and discussion of software quality. Their use in this academic project does not imply that PyTodo Pro is formally certified against these standards.

## 10. Project Deliverables

The overall project produces the following deliverables:

- Application overview and requirements analysis.
- Test plan and risk assessment.
- Black-box test cases and execution results.
- White-box test cases and code coverage analysis.
- Automated test scripts and execution results.
- GUI, usability and accessibility evaluation.
- API test cases and results.
- Security test cases and STRIDE analysis.
- Performance testing findings and measurements.
- Requirements Traceability Matrix.
- Consolidated defect log.
- Test execution summary and quality metrics.
- Integrated software quality evaluation.
- Final QA report.
- Project presentation and demonstration.

## 11. Important Notes

- This repository documents the quality evaluation of PyTodo Pro; it is not intended to serve as a replacement or modified version of the original application.
- Test results reflect the environment and conditions under which the tests were executed.
- A passed test case only confirms that the tested condition produced the expected result; it does not guarantee that the entire application is defect-free.
- Identified defects and recommendations should be interpreted according to their documented severity, impact and testing evidence.
- Any proposed improvements that have not been implemented and retested must be treated as recommendations rather than completed fixes.

## 12. Conclusion

This project demonstrates the practical application of Software Testing and Quality Assurance concepts through a structured evaluation of PyTodo Pro.

By combining manual and automated testing, functional and structural techniques, GUI and API evaluation, security analysis, performance measurement and quality assessment, the project provides a broader understanding of the application's strengths, weaknesses and potential risks.

The repository serves as the central reference for the team's testing artefacts, findings and documentation, supporting transparency, traceability and reproducibility throughout the quality assurance investigation.

