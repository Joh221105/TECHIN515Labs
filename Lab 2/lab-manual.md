# Week 2 Lab Manual: Anatomy of Coding Agents


## Table of Contents

1. [Overview](#overview)
2. [Learning Objectives](#learning-objectives)
3. [Pre-Lab Checklist](#pre-lab-checklist)
4. [Component A: Staff Interview](#component-a-staff-interview)
5. [Component B: Structured Lab](#component-b-lab)
6. [Component C: System Architecture & Design](#component-c-system-architecture--design)
7. [Component D: Testing & Validation](#component-d-testing--validation)
8. [Component E: Applied Challenge — The Prompt Showdown](#component-e-applied-challenge--the-prompt-showdown)
9. [Troubleshooting Matrix](#troubleshooting-matrix)
10. [Submission](#submission)
11. [Reflection](#reflection)

---

## Overview

This week focuses on understanding the anatomy of AI coding agents: how they work, how to talk to them effectively, and how to configure them for your project.

You will set up Claude Code or equivalence, explore Cursor's three editing modes (Composer, Chat, and Inline Edit), practice iterative prompt engineering, and create configuration files that give AI tools persistent context about your project. The lab begins with a staff interview that connects conditional logic in real-world advising to the structured prompting you will practice throughout the session.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. **Set up and use Claude Code** as a terminal-based AI coding agent, including API key configuration and basic commands
2. **Use Cursor's three editing modes** for different tasks and explain when to use each
3. **Write effective prompts** that produce accurate results, and iteratively refine prompts when the output does not match your intent
4. **Create project configuration files** (`.cursorrules` and `CLAUDE.md`) that provide AI tools with the context they need to produce consistent, high-quality output
5. **Compare AI tool outputs** by testing the same prompt across different tools and articulating differences in code style, explanation quality, and error handling
6. **Draw a flowchart** of the conditional logic from the staff interview, showing decision points and branches with labeled inputs and outputs
7. **Test configuration file effectiveness** by running the same prompt before and after adding `.cursorrules`, documenting differences in output quality

---

## Pre-Lab Checklist

This checklist is for your reference, but not for submission.
Before you begin, confirm the following:

- [ ] You have Cursor installed and can open a project folder in it
- [ ] You have a GitHub account and can push code to a repository
- [ ] `python3 --version` (or `python --version`) prints 3.11 or higher
- [ ] `streamlit --version` prints a version number (inside your virtual environment)
- [ ] You know how to activate your virtual environment (`source .venv/bin/activate`)
- [ ] You have a working Streamlit app from Week 1 (or you will use the provided starter app)
- [ ] You have created an Anthropic account at [https://console.anthropic.com](https://console.anthropic.com)
- [ ] You have an Anthropic API key ready or subscription (see Level 1 for setup instructions if you do not have one yet)
- [ ] (Optional) You have Node.js installed -- run `node --version` to check. If not installed, go to [https://nodejs.org](https://nodejs.org) and download the LTS version (v20+).

---

## Component A: Staff Interview

### Guest

**Jason Evans, Academic Student Counselor (ASC)** — Course Petition Syllabus Reviews

### Focus

Jason handles course petition syllabus reviews. This is a multi-step approval workflow involving gathering documents, combining them for review, and checking whether external syllabi match TECHIN course equivalencies. 

### During Interview

1. The interviewee addresses questions from class
2. Every student takes their own individual notes 
3. After the interview, you complete the synthesis artifact (an If-Then flowchart) individually
4. **Map the Emotional Journey**

   As you listen to the interviewee describe their workflow, pay attention to *how they feel* at each step, not just what they do. Mark moments on your notes with one of these three labels:

   - **Frustration peak** -- Where does the interviewee sound annoyed, defeated, or resigned? What specific moment causes the most friction? (Example: "Every quarter I answer the same 15 questions from different students, and I know there has to be a better way.")
   - **Delight moment** -- Where does the interviewee sound proud, satisfied, or relieved? What part of their workflow actually works well? (Example: "When I can pull up the right info instantly, students leave my office feeling confident about their plan.")
   - **Uncertainty zone** -- Where does the interviewee hesitate, say "it depends," or describe inconsistent processes? These zones signal opportunities for better information architecture.

   After the interview, color code these moments on the workflow. Label your colors.

   **Why this matters for design:** Your app should reduce frustration peaks and preserve delight moments. A common mistake is building technology that replaces a delightful human interaction with a sterile automated one. The emotional map helps you avoid that trap. It informs how to solve the problem without harming experience.


### Synthesis Artifact: Problem Statement and Flowchart

After the interview, write one sentence in this format:

> "When **[people]** needs to **[task]**, they currently **[workaround]**, which causes **[pain]**."


Based on interview, draw a flowchart for the workflow described by interviewee. Color code emotional journey on flowchart.


### Individual Deliverables

- Interview scripts and your own notes
- Problem statement and flowchart 

---

## Component B: Lab

> **Recall Prompt:** Before writing your first prompt today, recall the problem statement you wrote last week. How would you use that same format to describe what you want the AI to build?

### Warm-up — Level 2: Model Comparison

**Model Mapping:** Before starting the lab, complete this quick exercise.

Test the **same prompt** across 2 AI models (for example, Claude in Cursor vs. ChatGPT, or Claude Code vs. Copilot). Use a simple coding prompt like:

```
Write a Python function that takes a list of student records (dictionaries with
"name", "program", and "gpa" keys) and returns only the students in a given
program with a GPA above a given threshold. Include error handling.
```

Note the differences in:
- **Code style:** Variable naming, structure, comments
- **Explanation quality:** How well each model explains what it wrote
- **Error handling:** What edge cases each model anticipates

Write down 2-3 observations. You will reference these in your reflection.

---

### Level 1: Claude Code Setup

This section gets Claude Code installed and running. Claude Code is a terminal-based AI coding agent.

#### Step 1.1: Verify Your Week 1 Setup

Open your terminal (Terminal on macOS, Git Bash on Windows) and run each of these commands. Confirm you see the expected output.

```bash
git --version
```

Expected: a version number like `git version 2.43.0`.

```bash
python3 --version
```

Expected: `Python 3.11.x` or `Python 3.12.x`. On Windows, try `python --version` if `python3` does not work.

```bash
streamlit --version
```

Expected: a version number like `1.30.0` or higher.

```bash
node --version
```

Expected: `v20.x.x` or higher. If Node.js is not installed or below v20, download it now from [https://nodejs.org](https://nodejs.org) (choose the LTS version) and run the installer.

#### Step 1.2: Create an Anthropic API Key

Claude Code runs in your terminal and connects to Anthropic's API. You need an API key to use it.

1. Go to [https://console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to **Settings > API Keys** (or look for "API Keys" in the left sidebar)
4. Click **Create Key**
5. Give it a name like `techin510` and click **Create**
6. **Copy the key immediately.** You will not be able to see it again after you leave this page. Paste it somewhere safe (a password manager, a private note -- never in a file that gets pushed to GitHub).

> **Cost note:** Claude Code uses the Anthropic API on a pay-per-use basis. Typical coursework costs $5-15 per month. If you add $10 of credit to your account, that is enough to get started. If cost is a concern, contact the instructor privately.


#### Step 1.3: Install Claude Code

Follow Claude Code doc and install it.

This should install Claude Code globally on your machine. 

Verify the installation:

```bash
claude --version
```

Expected: a version number.


#### Step 1.4: Launch Claude Code in Your Project

Navigate to your Week 1 app folder (or any project folder) in the terminal. For example (the command varies depending on where the project lives in your device):

```bash
cd ~/Documents/techin510/my-first-app
```

Then start Claude Code:

```bash
claude
```

Claude Code will start an interactive session in your terminal. The first time you run it, it will ask you to authenticate. Follow the prompts -- you will either paste your API key or log in via browser.

Once authenticated, you should see a prompt where you can type natural language instructions. Try a simple test:

```
What files are in this project? Give me a brief summary.
```

Claude Code will read your project files and respond with a summary. You are now inside an agentic coding session -- Claude Code can read, write, and modify files across your entire project.

Type `/exit` to end the session for now. We will use it extensively in Levels 3 and 4.

---

**Checkpoint: Before moving on, confirm all of the following:**

- [ ] All Week 1 tools are working (Git, Python, Streamlit, Cursor)
- [ ] Node.js is installed (`node --version` returns 20+)
- [ ] You have an Anthropic API key stored securely (if you used API)
- [ ] Claude Code is installed (`claude --version` works)
- [ ] You successfully launched Claude Code in a project folder and got a response

---

### Level 2: Three Cursor Modes

In this level, you will use three different Cursor modes to add a feature, understand code, and refactor a function. This builds your muscle memory for choosing the right mode for the right task.

#### Step 2.1: Open Your Project in Cursor

Open your Week 1 Streamlit app in Cursor (File > Open Folder). Make sure your virtual environment is activated first:

```bash
cd ~/Documents/techin510/my-first-app
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate.bat  # Windows
```

#### Step 2.2: Add a Feature with Composer (Agent Mode)

Open Cursor Composer: press `Cmd+I` (macOS) or `Ctrl+I` (Windows).

Think of a prompt to improve your app. For example, if you built a Tip Calculator:
```
Add a new "Receipt Summary" section below the existing calculator. It should
display a formatted receipt that shows the date, bill amount, tip percentage,
tip amount, total, and per-person amount. Style it to look like a printed
receipt with a monospaced font. Add a "Copy to Clipboard" button.
```

If you built a Reading List Tracker:
```
Add a "Reading Stats" page to the app. Use st.sidebar to add navigation
between the main page and the stats page. The stats page should show: total
books added, a pie chart of books by status, the most recently added book,
and an "Export to CSV" download button.
```

Press Enter to submit the prompt. Review the generated code before accepting:

- Does the new feature appear in the code?
- Are there any obvious errors (missing imports, broken indentation)?
- Does the structure make sense at a glance?

Click "Accept" after reviewing the code and run the app to test:

```bash
streamlit run app.py
```

> **If the app does not run:** Copy the error message, go back to Composer (`Cmd+I`), paste the error, and say: "I got this error when running the app. Please fix it." This is the standard agentic debugging workflow.

#### Step 2.3: Understand Code with Chat (`Cmd+L`)

Now, find a part of the code you do not fully understand. Maybe it is the new feature you just added, or something from Week 1 that still looks unfamiliar.

1. Select (highlight) that section of code
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows) to open Cursor Chat
3. Type:

```
Explain this code to me step by step. I am a graduate student learning
to code. What does each line do, and why is it written this way?
```

Read the explanation carefully. If something is still unclear, ask a follow-up:

```
What does st.session_state do here? Why do we need it?
```

or

```
What would happen if I removed the try/except block?
```

#### Step 2.4: Refactor with Inline Edit

Pick a specific function or block of code that could be improved. Select it, then press `Cmd+K` (macOS) or `Ctrl+K` (Windows). This opens Cursor's inline edit mode -- it edits just the selected code rather than working across the whole project.

Try one of these prompts:

```
Refactor this to use a dictionary instead of multiple if/elif statements
```

```
Add error handling so this does not crash if the user enters invalid input
```

```
Rename the variables to be more descriptive and add comments explaining the logic
```

Review the proposed change, accept it, and verify the app still runs.

---

**Checkpoint: Before moving on, confirm:**

- [ ] You added a new feature to your app using Cursor Composer
- [ ] You used Chat (`Cmd+L`) to understand a section of code
- [ ] You used Inline Edit (`Cmd+K`) to refactor a specific function or block
- [ ] Your app runs without errors

---

### Information Hierarchy Review 

Before moving to Level 3 (Prompt Engineering Workshop), pause and evaluate your app's **visual hierarchy** .

**What is visual hierarchy?** It is the arrangement of elements on a page so that the most important information is seen first. A well-designed hierarchy guides the user's eye naturally from the most important content to the least important. A poor hierarchy makes everything look equally (un)important, so users do not know where to start.

**Step 1: The Squint Test**

1. Open your Streamlit app in the browser
2. Lean back from your screen and squint until the text blurs
3. What stands out? The elements you can still distinguish are the ones with the strongest visual weight
4. Write down the top 3 elements that stand out most when squinting

**Step 2: Evaluate Your Hierarchy**

Answer these questions about your app:

| Question | Your Answer |
|----------|-------------|
| What is the most important piece of information on the page? | |
| Is that information the most visually prominent element? | Yes / No |
| Can a first-time user understand what this app does at a glance? | Yes / No |
| Are related items visually grouped together? | Yes / No |
| Is there any element that draws attention but is not important? | Yes / No -- describe it |

**Step 3: Make One Hierarchy Fix**

Based on your evaluation, make one change to improve the hierarchy. Common fixes:

- Move the most important information higher on the page (above the fold -- the area visible without scrolling)
- Use `st.header()` instead of `st.write()` for section titles to create clearer visual separation
- Remove or de-emphasize decorative elements that compete with important content
- Group related controls together using `st.sidebar` or `st.columns()`
- Add whitespace between sections using `st.divider()` or `st.markdown("---")` to create breathing room

**Record your change.** Write one sentence describing what you changed and why. Add this to your AI Usage Log.

---

### Level 3: Prompt Engineering Workshop

Prompt engineering is the skill of communicating your intent to AI tools precisely enough to get the result you want. In this level, you will practice writing, testing, and refining prompts through three iterations.

#### Step 3.1: Write a Spec First

Before writing any prompt, practice the **spec-first habit**. For each prompt attempt, write a 3-sentence specification:

1. **What should it do?** (behavior and purpose)
2. **What inputs does it take?** (data, user actions, parameters)
3. **What should the output look like?** (visual layout, format, interaction)

Write your spec in a comment at the top of your file or in a separate note. Then use your spec to write the prompt. After each attempt, compare the result to your spec (not just to the visual target. Did the AI deliver what you specified?)

> A clear spec produces better AI output than ad-hoc prompting.

#### Step 3.2: Attempt 1 -- Vague Prompt

Open Cursor (`Cmd+I`) and write a prompt to add a new feature to your app. For your first attempt, keep it **deliberately vague**. For example:

```
Add a chart to my app
```

or

```
Make the app look better
```

Submit the prompt and see what happens. Note what the AI assumed, what it got wrong, and what was missing.

**Record this prompt and the result.** This is prompt 1 of 3 for your prompt log.

#### Step 3.3: Attempt 2 -- Specific Prompt

Now rewrite the prompt with specifics. Add details about:
- **Layout:** Where should the element appear? What size?
- **Data:** What data should be displayed? What format?
- **Styling:** Colors, fonts, spacing
- **Behavior:** What happens on interaction?

For example:

```
Add a bar chart below the main content showing the top 5 items by count.
Use Plotly with a blue color palette. Include a title "Top 5 Items",
label both axes, and add hover tooltips showing the exact count.
```

Submit and compare the result to your vague prompt. What improved?

**Record this prompt and the result.** This is prompt 2 of 3 for your prompt log.

#### Step 3.4: Attempt 3 -- Constrained Prompt

For your third attempt, add constraints that eliminate ambiguity:

- Specify the exact technology (Plotly, not Matplotlib)
- Specify error handling behavior
- Specify edge cases ("if the data is empty, show a friendly message instead of an empty chart")
- Reference your project's conventions ("follow the coding standards in .cursorrules")

For example:

```
Add a bar chart below the main content section using Plotly (not Matplotlib).
Show the top 5 items sorted by count in descending order. Use the color
palette from .cursorrules. Title: "Top 5 Items". X-axis: item names.
Y-axis: "Count". Add hover tooltips with exact values. If there are fewer
than 5 items, show however many exist. If the data is empty, display
st.info("No data to display yet.") instead of an empty chart. Use
st.cache_data on the data preparation function.
```

Submit and compare all three results side by side.

**Record this prompt and the result.** This is prompt 3 of 3 for your prompt log.

#### Step 3.5: Reflect on the Progression

Look at your three attempts and note:

1. What was the biggest difference between your vague and specific prompts?
2. What kind of detail mattered most -- layout, data, styling, or behavior?
3. How much of the final result came from your instructions versus the AI's assumptions?

---

### Level 4: Configuration Files

Configuration files are how you give AI tools persistent context about your project. Think of them as the "brief" you hand to a new collaborator on their first day. Without them, AI tools start every conversation from scratch. With them, they understand your project's standards, preferences, and structure from the start.

#### Step 4.1: Create a Cursor Rules

In Cursor, create Cursor rules. Add the following content, customizing it for your project:

```
# Project: [Your App Name]
# Framework: Streamlit (Python)
# Python version: 3.11+

## Coding Standards
- Use Python 3.11+ features and syntax
- Use type hints for function parameters and return values
- Add docstrings to all functions (Google style)
- Use descriptive variable names (avoid single-letter names except for loop counters)
- Keep functions under 30 lines; extract helper functions when needed

## Streamlit Conventions
- Use st.set_page_config() at the top of the main app file
- Organize the UI with st.sidebar for controls and the main area for display
- Use st.cache_data for expensive computations
- Handle errors gracefully with try/except and display user-friendly messages with st.error() or st.warning()

## Project Structure
- app.py: Main Streamlit application
- utils.py: Utility functions and data processing
- data/: Directory for data files (CSV, JSON)

## Visualization
- Prefer Plotly for interactive charts
- Use a consistent color palette: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
- Always include chart titles, axis labels, and legends
```

Save the file. Now, when you use Cursor in this project, it will read this file and follow your instructions.


> **Design connection:** Think of rules as a design system for your AI collaborator. Just as a design system ensures consistency across a product (same colors, same spacing, same typography), rules ensure consistency across AI-generated code (same style, same conventions, same patterns).

#### Step 4.2: Create a `CLAUDE.md` File

`CLAUDE.md` serves the same purpose as `.cursorrules` but for Claude Code. Create a new file in your project root called `CLAUDE.md`:

```markdown
# Project Context

## What This Project Is
[One sentence describing your app. Example: "A Streamlit web app that tracks
personal reading lists with status management and summary statistics."]

## Tech Stack
- Python 3.11+
- Streamlit for the web interface
- Plotly for interactive charts
- Pandas for data manipulation

## Project Structure
- `app.py` -- Main application entry point
- `utils.py` -- Utility functions and helpers
- `data/` -- Data files
- `.cursorrules` -- Cursor AI configuration

## Development Commands
- Run the app: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt`

## Coding Standards
- Follow PEP 8 style guidelines
- Use type hints on all function signatures
- Write Google-style docstrings for all functions
- Handle errors gracefully; never let the app crash on user input
- Never hardcode sensitive data (API keys, passwords)

## Important Notes
- This is a course project for TECHIN 510 at UW GIX
- The audience for this app is [describe your target users]
- When making changes, always verify the app still runs with `streamlit run app.py`
```

Customize this for your project, then save.

**What success looks like:** A `CLAUDE.md` file exists in your project root with accurate information about your project. You wrote the project description and target audience in your own words.

#### Step 4.3: Test Your Configuration Files

Let us verify that the configuration files actually change how the AI behaves.

**Test Cursor Rules** Open Cursor Composer (`Cmd+I`) and type:

```
Add a new helper function to utils.py that takes a list of numbers and
returns the mean, median, and standard deviation as a dictionary.
```

Check: Does the generated code follow your rules? Does it have type hints, a docstring, and descriptive variable names?

**Test `CLAUDE.md`:** Open Claude Code in your terminal:

```bash
cd ~/Documents/techin510/my-first-app
claude
```

Then type:

```
What is this project? What tech stack does it use?
```

Claude Code should answer based on the `CLAUDE.md` file you created, without needing to analyze every source file.

**What success looks like:** Both AI tools reference your configuration files and produce output that follows your stated conventions.


#### Step 4.4: Commit and Push

Commit everything and push to GitHub. Make sure your README clearly documents the project and provides step-by-step instructions on how to produce all results.

---

### Level 5: Stretch Goals

Implement one of these structured challenges:

**Option A: Multi-File Refactor with Claude Code**
- **Goal:** Use Claude Code to split your `app.py` into multiple files: `app.py` (UI only), `utils.py` (helper functions), and `data.py` (data handling).
- **Guiding prompt:** "Refactor app.py into three files: app.py for UI, utils.py for helper functions, and data.py for data loading. Keep imports clean."
- **Checkpoint:** Your app still runs after refactoring, and each file has a clear single responsibility.

**Option B: Compare 3 Models on the Same Task**
- **Goal:** Extend your warm-up by testing 3 different models (e.g., Claude, ChatGPT, Gemini) on the same coding task. Create a comparison table.
- **Checkpoint:** A markdown table comparing code style, explanation quality, and error handling across 3 models.

---

**Checkpoint: Before finishing, confirm:**

- [ ] You enhanced your app with 2+ features using Claude Code and/or Cursor
- [ ] You have a `.cursorrules` file customized for your project
- [ ] You have a `CLAUDE.md` file with accurate project context
- [ ] You tested both configuration files and saw the AI tools reference them
- [ ] You have a prompt log showing 3 prompts (vague, specific, constrained) with before/after results
- [ ] All changes are committed and pushed to GitHub

---

## Component C: System Architecture & Design

---

### C.1 Architecture Concept: Components & Boundaries

#### The Big Idea

When you build software, not everything is "your code." Your project is a collection of **components** (distinct pieces that each have a job) and the lines between them are called **boundaries**. Understanding where your code ends and someone else's system begins is one of the most important skills in software architecture.

In software:

- **Your code:** The Python you wrote in `app.py` -- you own this completely.
- **Cursor / Claude Code:** AI tools that help you write code. They generate suggestions, but you accept or reject them. The boundary is: they propose, you decide.
- **External APIs / libraries:** Streamlit, Plotly, GitHub. You call them, but you do not control how they work internally.
- **GitHub:** Stores your code remotely. You push to it, but GitHub handles storage, access control, and versioning.

#### Connection to Today's Lab

Today you configured `.cursorrules` and `CLAUDE.md` files. These files sit exactly on the boundary between your code and your AI tools. They are YOUR instructions to THEIR system. Understanding this boundary helps you:

- Write better configuration files (because you know what the AI tool can and cannot see)
- Debug faster (because you know whether a problem is in your code or in the tool's behavior)
- Make deliberate choices about what context to give the AI versus what to handle yourself

---

### Design Decision Log 

#### The Template

| Field | Your Entry |
|-------|------------|
| **Decision** | What did you decide? |
| **Alternatives considered** | What else could you have done? |
| **Why you chose this** | What constraint drove it? |
| **Trade-off** | What did you give up? |
| **When would you choose differently?** | Under what conditions? |

#### This Week's Decision Prompt

> **"Where should project context live -- in `.cursorrules`, in `CLAUDE.md`, in your prompts, or in all three?"**

Think about:
- What happens when you put instructions in `.cursorrules` versus typing them into every prompt?
- What if your `.cursorrules` says "use Plotly" but your prompt says "use Matplotlib"? Which wins?
- Is there information that belongs in one place but not the other?
- What is the cost of maintaining context in multiple places versus one?

## Component D: Testing & Validation

> This week you set up `.cursorrules` and `CLAUDE.md` configuration files. A natural question follows: did those files actually change the AI's behavior? This exercise introduces **regression testing** -- checking whether a change you made (the config files) affected something that was already working (your prompts).

---

### Validation Exercise: Prompt Regression Test

#### What you are testing

In Component B, you created `.cursorrules` and `CLAUDE.md` files to give AI tools persistent context about your project. Now you will test whether those configuration files actually changed the output. This is a form of regression testing: you re-run the same inputs and check whether the outputs changed -- and whether the change was an improvement, a regression, or neutral.

Before comparing "without config" vs. "with config" outputs, run a quick smoke test for each generated result. 

#### Instructions

**Gather 3 prompts from Week 1 or today's lab**

Pick 3 prompts you used in Cursor during Week 1 or during today's Level 2/Level 3 exercises. Good candidates:

- A prompt that asked Cursor to add a feature
- A prompt that asked Cursor to explain code
- A prompt that asked Cursor to fix a bug

Write each prompt down exactly as you used it (or as close as you can remember).

**Step 2: Run each prompt WITHOUT your config files**

Temporarily rename your configuration files so the AI tools do not see them:

```bash
# In your project directory
mv .cursorrules .cursorrules.bak
# If you have a CLAUDE.md file, rename it too
mv CLAUDE.md CLAUDE.md.bak
```

Open Cursor, restart it (close and reopen your project so it does not cache the old config), and run each of your 3 prompts. For each one, briefly note:

- What code or explanation did Cursor produce?
- Did it follow your project's conventions (type hints, docstrings, Streamlit patterns)?
- How long/detailed was the response?

**Step 3: Run each prompt WITH your config files**

Restore your configuration files:

```bash
mv .cursorrules.bak .cursorrules
mv CLAUDE.md.bak CLAUDE.md
```

Restart Cursor again (close and reopen the project). Run the same 3 prompts and note the differences.

**Step 4: Record your results**

Use the recording template below.

#### Recording Template

Copy this table into your submission document and fill it in for each of your 3 prompts:

| # | Prompt Used | Without Config (Before) | With Config (After) | What Changed | Better/Worse/Same |
|---|-------------|------------------------|--------------------|--------------|--------------------|
| 1 | _e.g., "Add a search bar to filter FAQs"_ | _Generated basic search with no type hints, no docstring_ | _Generated search with type hints, Google-style docstring, used st.cache_data_ | _Added type hints and caching per my .cursorrules_ | _Better_ |
| 2 | _e.g., "Explain the filter function"_ | _Generic explanation, no project context_ | _Referenced "GIX Student Guide" and explained in terms of FAQ filtering_ | _Used project context from CLAUDE.md_ | _Better_ |
| 3 | _e.g., "Add error handling"_ | _Added basic try/except_ | _Added try/except with st.error() messages and logging_ | _Followed Streamlit conventions from config_ | _Better_ |

---

### D.2 Quality Gate

Before you submit, every item below must be satisfied:

- [ ] **Smoke test completed**: For each prompt output, you confirmed (1) it runs, (2) the core behavior works once, and (3) invalid input is handled without crashing
- [ ] **3 prompts tested**: Your recording template has 3 complete rows with before/after observations
- [ ] **Differences are specific**: Each "What Changed" entry describes a concrete, observable change (e.g., "added type hints" not "output improved")
- [ ] **Config files restored**: Your `.cursorrules` and `CLAUDE.md` files are back in place and working (run one prompt to verify)
- [ ] **Honest assessment**: If a config file made no difference on a particular prompt, you documented that honestly (marking "Same")
- [ ] **Prompts are documented**: The exact prompt text is recorded so someone else could reproduce the test

---

### Testing Concept Preview: Regression Testing

#### What is a regression test?

In software, a regression test re-runs existing tests or checks after a change to make sure the change did not break something that was previously working. A regression is when something that used to work stops working because of a new change.

#### Why this matters

- In professional software development, regression tests run automatically every time someone changes the code
- AI-generated code is especially prone to regressions: when you ask the AI to add a feature, it might accidentally break an existing feature in the process
- Configuration files (`.cursorrules`, `CLAUDE.md`) are themselves a form of input to the AI -- changing them can regress or improve the AI's output, just like changing code can regress or improve your application. This is exactly what professional teams do, except they automate it.

---

## Component E: Applied Challenge — The Prompt Showdown

### The Problem

GIX Career Services wants a "Quick Eligibility Checker" widget — students enter their program, graduation quarter, and CPT status, and the tool shows which career events (mock interviews, resume reviews, employer panels, networking nights) they qualify for. Your job: write a spec, give the identical spec to two AI coding tools, and compare the results.

### What You Build

- A 5-sentence specification document describing the eligibility checker
- Two implementations generated by two different AI tools (e.g., ChatGPT + Cursor, Copilot + Claude)
- A `.cursorrules` file (or equivalent project-level AI config) that improves output quality
- A comparison table evaluating both implementations
- A decision flowchart for the eligibility logic

### Part 1: Architecture & Design

1. **Flowchart:** Draw a decision flowchart for the eligibility logic with at least 3 decision branches. Annotate where a **human review** step belongs — edge cases the tool shouldn't auto-decide.
2. **Spec:** Write a 5-sentence specification. The spec should be precise enough for an AI tool to implement without additional clarification.

### Part 2: Implementation

1. Give your **identical spec** to two different AI coding tools
2. Save both outputs as separate files
3. Create a `.cursorrules` file (or equivalent) that improves the quality of AI-generated code for this project
4. Re-run one of the tools with `.cursorrules` active and note any differences

### Part 3: Testing & Validation

1. **Comparison table:** Create a table comparing the two implementations across dimensions you consider most important
2. **Smoke test first:** For each implementation, confirm it starts/runs, one core path works, and invalid input does not crash the app.
3. **Input testing:** Test each implementation with 1 valid input and 1 invalid input. Document the results.

---

## Troubleshooting Matrix

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `npm: command not found` | Node.js is not installed or not on your PATH | Download from [https://nodejs.org](https://nodejs.org) (LTS version). Close and reopen your terminal after installing. |
| Permission denied when installing Claude Code (macOS) | npm global install needs elevated permissions | Try `sudo npm install -g @anthropic-ai/claude-code` and enter your system password. If that fails, try `npm install -g @anthropic-ai/claude-code --prefix ~/.local` and add `~/.local/bin` to your PATH. |
| Permission denied when installing Claude Code (Windows) | Terminal not running as administrator | Open Git Bash or Command Prompt as Administrator (right-click > Run as administrator), then run the install command again. |
| Claude Code installs but `claude` command is not found | npm global bin directory not on PATH | Run `npm bin -g` to see where global packages are installed, then add that directory to your PATH. Ask a TA for help if needed. |
| "Invalid API key" or "Authentication failed" | API key was copied incorrectly or is inactive | Verify the key starts with `sk-ant-`, has no extra spaces, and is active in your Anthropic Console (console.anthropic.com > API Keys). If exposed, revoke immediately and create a new one. |
| "Insufficient credits" or "Rate limit exceeded" | Anthropic account needs credits | Go to console.anthropic.com > Settings > Billing and add credit. $10-15 is sufficient for several weeks. |
| Claude Code asks for authentication every time | API key not saved persistently | Run `claude config set apiKey <your-key>` to save it, or set the environment variable: `export ANTHROPIC_API_KEY=sk-ant-your-key-here` (add to `~/.bashrc` or `~/.zshrc` for permanence). |
| `.cursorrules` not being picked up by Cursor | File not in project root, or Cursor needs restart | Verify the file is in the top-level folder you opened in Cursor (not in a subfolder). File name must be exactly `.cursorrules` with the leading dot and no extension. Restart Cursor after creating the file. |
| Cursor Composer does not follow `.cursorrules` | Cursor did not detect the file on startup | Close and reopen the project in Cursor. Verify the file appears in Cursor's file explorer sidebar. |
| Cursor Chat (`Cmd+L`) does not see selected code | Code was not highlighted before opening Chat | Highlight the code first, then press `Cmd+L`. You can also use @-mentions: type `@` in Chat and select a file to include it explicitly. |
| "Model not available" or slow Cursor responses | Internet connection issue or model unavailable | Check your internet connection. Try selecting a different model from the model dropdown in Composer or Chat. |
| App crashes after refactoring with Claude Code | Import error from file restructuring | Check that `app.py` imports from `utils.py` correctly: `from utils import function_name`. Verify both files are in the same directory. |
| `ModuleNotFoundError: No module named 'utils'` | `utils.py` not in the same folder as `app.py` | Ensure `utils.py` is in the same directory. When running `streamlit run app.py`, make sure your terminal is in the project folder. |
| Streamlit changes do not appear in browser | Auto-reload did not trigger | Click "Rerun" in the top right of the Streamlit app, or stop (`Ctrl+C`) and restart (`streamlit run app.py`). |
| Cursor mode switching confusion | Using the wrong mode for the task | Remember: `Cmd+I` = Composer (generate), `Cmd+L` = Chat (understand), `Cmd+K` = Inline Edit (refactor). See the summary table in Level 2. |

---

## Submission

All deliverables are **individual**. Submit your GitHub repo link on Canvas. Your GitHub repo should be well organized. Results should be reproducible with clear instructions on how to run the code. Make sure your repo contains a PDF report with the following information:

Your repo must include your Streamlit source code, `requirements.txt`, and a README with clear run instructions.

### Component A Deliverables

1. **Interview scripts** with your own notes from the staff interview
2. **Problem statement and flowchart**

### Component B Deliverables

1. **AI Usage Log & Prompt Log — Level 1: Descriptive** (continued from Week 1): Include your 3 prompts (vague, specific, constrained) with before/after results. For each, write: Prompt -> Output -> What it did. This single document covers both deliverables.
2. **Screenshot** of your enhanced app running

### Component C Deliverables

1. Architecture diagram
2. Design Decision Log

### Component D Deliverables

1. **Validation results** (completed validation evidence)
2. **Quality gate checklist** (completed)

### Component E Deliverables

1. **5-sentence specification document** for the eligibility checker
2. **Two implementations** generated by two different AI coding tools (saved as separate files)
3. **Project-level AI configuration file** (`.cursorrules` or equivalent)
4. **Comparison table** evaluating both implementations
5. **Decision flowchart** for the eligibility logic (including at least 3 branches and a human review step)
6. **Smoke test evidence** for each implementation (runs, core path works, invalid input handled without crash)
7. **Input testing evidence** for each implementation (1 valid input and 1 invalid input, with results)

### Reflection Deliverables

Submit **3-5 sentences** addressing the Reflection questions below as part of your Week 2 deliverables.

---

## Reflection

Write 3-5 sentences addressing these questions. Include this in your Canvas submission.

1. **Tool comparison:** When you tested the same prompt across different AI tools (the AI Fluency warm-up or Cursor vs. Claude Code during the lab), what differences did you notice? Which tool gave you better code, and which gave you a better explanation?

2. **Prompt quality:** Look at your prompt log. What specifically changed between your vague first prompt and your constrained third prompt? What did you learn about what AI tools need from you to produce good results?

3. **Configuration impact:** After creating `.cursorrules` and `CLAUDE.md`, did you notice any change in the output you got from AI tools? How do configuration files change the way an AI coding agent behaves -- and what would you add to these files after today's experience?
