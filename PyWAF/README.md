# PyWAF (Python Web Application Firewall)

![Language](https://img.shields.io/badge/Language-Python%203-blue?style=flat-square&logo=python)
![Type](https://img.shields.io/badge/Type-Reverse%20Proxy-orange?style=flat-square)
![Category](https://img.shields.io/badge/Category-Application%20Security-red?style=flat-square)

## Overview

PyWAF is a custom-built, lightweight Web Application Firewall (WAF) designed to protect web servers from common Layer 7 attacks. Acting as a Reverse Proxy, PyWAF sits in front of the vulnerable application, intercepting all incoming HTTP requests. It performs Deep Packet Inspection on the request URL and body, using Regex-based signatures to detect and block malicious payloads—specifically targeting the OWASP Top 10 vulnerabilities like SQL Injection, Cross-Site Scripting (XSS), and Path Traversal—before they reach the backend server.

## Key Features

### 1. Reverse Proxy Engine
* Intercepts client traffic on port `9000` and forwards legitimate requests to the backend application on port `5000`.
* Hides the origin server's identity and provides a single point of entry for security filtering.

### 2. SQL Injection Defense
* Inspects query parameters for malicious SQL patterns.
* Blocks Keywords like `UNION`, `SELECT`, `--`, and hex sequences used to manipulate database queries.

### 3. XSS Mitigation
* Sanitizes and blocks requests containing malicious script tags.
* Blocks `<script>`, `javascript:`, `onerror`, and other event handlers used to execute arbitrary code in the browser.

### 4. Path Traversal Protection
* Prevents attackers from accessing unauthorized file system directories.
* Blocks Dot-dot-slash patterns (`../`, `..\`) and attempts to access sensitive system files (e.g., `/etc/passwd`).

### 5. Real-time Logging
* Logs every request details (IP, Timestamp, Payload) to the console.
* Alerts administrators immediately when a malicious request is intercepted (HTTP 403 Forbidden).

## Architecture

1.  **Client Request** 
    * The user sends a request to the WAF (`localhost:9000`).

2.  **Inspection** 
    * PyWAF analyzes the HTTP headers and payload against defined security rules.

3.  **Decision:**
    * The request is forwarded to the Vulnerable App (`localhost:5000`), and the response is sent back to the user if the requests is malicious The request is dropped immediately. PyWAF responds with a `403 Forbidden` error page.

## Demo & Proof of Concept

### 1. Normal Traffic
When a legitimate user searches for "halo", PyWAF inspects the packet, finds no threats, and forwards it to the backend. The server responds with `200 OK`.

![Normal Browser](screenshots/Normal_state.png)

![Normal Log](screenshots/Normal_state_terminal.png)

### 2. SQL Injection Attack
An attempt to inject SQL commands (`UNION SELECT`).
* Payload: `?q=union select`
* Status: `403 Forbidden`

![SQLi Browser](screenshots/SQLi_blocked.png)

![SQLi Log](screenshots/SQLi_blocked_terminal.png)

### 3. XSS Attack
An attempt to inject a JavaScript payload (`<script>alert(1)</script>`).
* Payload: `?q=<script>alert(1)</script>`
* Status: `403 Forbidden`

![XSS Browser](screenshots/xss_blocked.png)

![XSS Log](screenshots/xss_blocked_terminal.png)

### 4. Path Traversal Attack
An attempt to step back directories to read system files (`../etc/passwd`).
* Payload: `?q=../../etc/passwd`
* Status: `403 Forbidden`

![Path Traversal Browser](screenshots/path_traversal_blocked.png)

![Path Traversal Log](screenshots/path_traversal_blocked_terminal.png)

## Prerequisites

* Python 3+
* Flask

---
Created by: Yustinus Hendi Setyawan
Date: Monday, December 22 2025