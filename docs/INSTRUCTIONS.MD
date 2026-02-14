**Subject: Technical Specifications for AI-Managed Portfolio Website and Local AI Application**

Dear Development Agent,

This letter outlines the full technical specifications and constraints for the implementation of two connected systems:

1. A public-facing portfolio website advertising AI consulting services.
2. A separate locally run AI application capable of modifying the website’s content programmatically.

The goal is to create a zero-cost, fully static web presence that can be updated through conversation with a local AI model.

---

## 1. Portfolio Website (Public-Facing)

### 1.1 Hosting & Deployment

* Hosting platform: **GitHub Pages**
* Repository hosted on **GitHub**
* No backend server
* No paid services
* No subscriptions
* Fully static (HTML, CSS, JavaScript only)
* Zero operational cost

### 1.2 Purpose

The website must:

* Advertise AI consulting services
* Present:

  * Professional bio
  * Services offered
  * Projects or portfolio items
  * Contact information
* Maintain clean, modern, responsive design
* Be easily modifiable via structured content updates

### 1.3 Architecture Requirements

The site must:

* Separate **content from structure**
* Store editable content in structured format (e.g., JSON or Markdown files in the repo)
* Avoid hardcoding textual content inside HTML wherever possible
* Allow programmatic content replacement

Suggested structure:

```
/index.html
/css/
/js/
/content/
    bio.json
    services.json
    projects.json
```

### 1.4 Contact Form

* Contact form must be implemented using an embedded form service.
* The embed link will be provided from **Fillout**.
* Integration method: iframe embed or script embed.
* No custom backend handling.
* Form submissions must be handled entirely by Fillout.

---

## 2. Local AI Application (Private System)

### 2.1 Purpose

A locally run application that:

* Hosts an AI model
* Allows conversational interaction
* Modifies the portfolio website’s content files
* Commits and pushes changes to GitHub automatically

This application functions as a personal AI web manager.

### 2.2 Execution Environment

* Runs locally on user’s machine
* No cloud inference APIs
* No paid AI services
* May use:

  * Open-source local LLM (via Ollama or similar)
  * Node.js or Python runtime
* Zero cost

### 2.3 Capabilities

The application must:

1. Accept conversational instructions such as:

   * “Update my bio to mention I specialize in RAG systems.”
   * “Add a new project about chatbot automation.”
   * “Change my services to emphasize AI consulting for startups.”

2. Convert those instructions into:

   * Structured edits to JSON or Markdown files
   * Safe file modifications
   * Proper formatting preservation

3. Automatically:

   * Stage changes
   * Commit changes with descriptive commit message
   * Push to GitHub repository
   * Trigger GitHub Pages redeploy

---

## 3. MCP Tool Requirement

The AI application must expose or integrate an MCP-compatible tool with the following functionality:

### 3.1 MCP Tool: `update_website_content`

Responsibilities:

* Accept structured update payload:

  ```
  {
    "file": "bio.json",
    "operation": "replace" | "append" | "delete",
    "content": {...}
  }
  ```

* Validate file existence

* Apply safe modification

* Prevent corruption of structure

* Write changes to disk

* Optionally trigger Git operations

### 3.2 Safety Constraints

* No arbitrary shell execution from AI
* Only allow edits within designated `/content` directory
* Enforce JSON schema validation before write
* Provide rollback mechanism if formatting breaks

---

## 4. GitHub Automation Requirements

The local app must:

* Authenticate with GitHub using:

  * Personal Access Token (stored securely in environment variables)
* Perform:

  * `git add`
  * `git commit -m "AI update: ..."`
  * `git push`
* Handle errors gracefully
* Confirm deployment status

---

## 5. System Design Principles

* Zero-cost architecture
* Fully static deployment
* No backend servers
* No hosting beyond GitHub Pages
* Content-driven architecture
* Local AI autonomy
* Deterministic file modification

---

## 6. Final Deliverables

1. Static portfolio site deployed on GitHub Pages.
2. Structured content folder for AI-editable text.
3. Local AI chat application.
4. MCP tool for safe content updates.
5. Git automation integration.
6. Embedded Fillout contact form.
7. Documentation explaining:

   * Setup
   * Environment variables
   * Deployment steps
   * Usage instructions

---

## 7. High-Level Objective

The final system must allow the user to:

* Speak naturally to a local AI.
* Have that AI update website content.
* Automatically deploy changes to GitHub Pages.
* Maintain a living, AI-managed web presence.
* Allow visitors to contact via embedded Fillout form.

This must be achieved with no ongoing cost, no servers, and no subscriptions.

---

Please treat this specification as binding architecture guidance and implement accordingly.

Sincerely,
AI Consulting Portfolio Project Owner
