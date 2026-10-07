# AI Prompts Log: HW4

Log of every prompt I typed to the AI assistant for HW4, recorded exactly as typed, grouped by problem. After each problem, a short note records what my original prompts were missing, if follow-ups were needed.

---

## Problem 1: Vibe coder prompts

### How this log is kept: the `/start-hw` skill

I built a custom Claude Code skill, `/start-hw`, that makes the AI assistant keep this log for me. I run it once at the start of a homework, and it:

- **Finds the homework folder.** It takes the homework name from the folder (here, `HW4`) and asks me which folder to use if that isn't clear.
- **Creates or reuses `AI_prompts.md`.** If the file already exists, it adds to it and never overwrites or reorders earlier entries.
- **Logs every prompt word for word.** For the rest of the session, it appends each prompt I type exactly as I typed it, typos and all, with no paraphrasing or fixes.
- **Groups prompts by problem.** Each problem gets a `## Problem N: <name>` heading, and prompts are numbered in order under it.
- **Leaves out anything I didn't type.** The assistant's answers and tool output are not logged, and pasted material shows up as a short `[pasted: ...]` note.
- **Reflects on each problem.** When a problem is done, it writes one sentence on what my original prompt was missing that made follow-ups necessary.

Having the assistant log each prompt as it goes means the record is complete and exact. I don't have to copy prompts over by hand afterward.

### Prompts

1. we're now working on homework 4. work only in the homework 4 folder a /start-hw
2. Problem 1 is "Vibe corder prompts". We've already done it with /start-hw, it is to set up the AI_prompts.md and keep the log. You know what should be done, right?
3. why don't you add something to problem 1 explainign the /start-hw skill

### What was lacking in my original prompt

My original prompt didn't name the problem or ask for an explanation of the `/start-hw` skill, so I needed follow-ups to label Problem 1 and add that explanation.

---

## Problem 2: Analyze the database

### Prompts

1. Problem 2 is "Analyze the database". Find the data.zip in the folder and unzip so we have data/campus_customs.db with tables catalogue, inventory, users and data/products/ with product images; paths should match the catalogue table.

Then look at the database and understand each field. Start output/harness.md. We'll then write down each table and its fields and a short line on why each field matters for the shop or the chatbot.

### What was lacking in my original prompt

_To be filled in once Problem 2 is complete._

---

## Problem 3: Build the campus customs website

### Prompts

1. Problem 3 "Build the campus customs website" 

We are going to create a React+Vite+TypeScript front end for campus customs. We should have a nav bar at the top taht links to Home, Products, About Us, Log in, and Create account. We should use wording similar to the wording on yalebulldogblue.com, but write in a different voice (don't copy the original site text). Make it preppy, Ivy style, focused on heritage and tradition, and pretend Yale is a football school (like USC).

On the Products page, we shoud show images from the catalogue with basic product info. Make each product open a single-item page (large image on the left, full product text on the right). Clicking a cared on Products would take us thehre. 

On the bottom right of the site, there should be a chat interface. It doesn't need to talk to an agent yet but should be a stub that will call the backend later. 

A simple FastAPI app will be needed in backend/main.py to read the database
2. can you load up the preview
3. i dont see anything

### What was lacking in my original prompt

My original prompt didn't ask the assistant to open the finished site in the preview pane for me, so I needed follow-ups to get it loaded and showing the frontend instead of the backend.

---

## Problem 4: Create account and login

### Prompts

1. okay nice lets move on to problem 4 "Create account and login". Create an account and log in. Add the new account (and all accounts) to the users table. Passwords should be stored securely. then open up the website and i'll test logging in. Then we'll update output/harness.md wiht how auth works (what we store for a user and how passwords are protected).
2. i want to creat  an account. also did that even work?
3. the site is not open
4. nice i created the accoutn and logged in. are the details in the users table?

### What was lacking in my original prompt

My original prompt didn't specify how to open the site for testing or how logged-in sessions should behave, so follow-ups were needed to get the preview showing and to confirm the new account landed in the users table.

---

## Problem 5: PydanticAI agent backend

### Prompts

1. cool lets move onto problem 5 "PydanticAI agent backend". I'm probably going to stop now and we'll continue tomorrow.
2. yeah shut them down
3. i'm back lets work on problem 5
4. how did you know what to do i never even gave you the prompt
5. well heres what you should be doing for problem 5. We want to build the chatbot as a pydanticai agent behind fastapi. The api app should be in backend/main.py. The agent should be four files: backend/prompts/prompt.md, backend/agent.py, backend/tools.py, backend/models.py. In main.py, expose a chate route so a message from the website returns a reply from the agent. usem yportkey_api_key. Use voice and safety basics in prompts/prompt.md. Start/update types in models.py for caht repleis as needed. In output/harness.md, note how the front end talks to fastapi and how the agent is loaded. the backend should run from the backend/ folder like uvicorn main:app --reload --port 8000. is this consistent with what you already did? if not, update to my instructions
6. alright im gonna comme back to this later wrap it up and make a record for next time. You should start hte next session when i do /start-hw
7. yes still in hw 4. did you do everything in problem 5 already?

### What was lacking in my original prompt

My first prompt gave only the title "PydanticAI agent backend", so I had to build from inferred requirements; the follow-up with the real spec (four-file layout in backend/, prompt.md for voice/safety, running from the backend/ folder) is what pinned down the structure and forced a refactor.

---

## Problem 6: Tools: Product Info and Stock

### Prompts

1. coolio yeah lets move onto problem 6. problem 6 is "Tools: Product Info and Stock". We're going to build the tools for the agent to look up product description, price, and stock from campus_customs.db. The agent must use the database, not invent prices or quantities. If a size is out of stock , it should say so clearly. Expand prompts/prompt.md so the agent knows to call these tools for price and stock questions. Add or update return types in models.py. In output/harness.md, list each tool and explain which model fields you chose for lookup results and why.
2. is it logged?
3. are we done with problem 6?
4. can you open it in my browser

### What was lacking in my original prompt

_To be filled in once Problem 6 is complete._

---

## Problem 7: Chat search that updates the page

### Prompts

1. okay moving onto problem 7 "Chat search that updates the page". When a customer asks about a type of item in the chat, the agent should search the catalogue and the website should dynamically show those matching items as product cards. After the dynamic product cards are loaded, the same single-item page behavior from problem 3 should still work. Update prompts/prompt.md and output/harness.md so it is clear how search results reach the page
2. nice bro i tested it and it looks good.

### What was lacking in my original prompt

My original prompt covered the goal well; the only gap was it did not anticipate that the agent would sometimes reply about a category without returning product_ids, which I had to make reliable so the page actually filled.

---

## Problem 8: Customer memory

### Prompts

1. Let's move onto problem 8 "Customer memory"

When a shopper is logged in, save their chat history in the database in an appropriate table and reload it when they return. the agent should know who is chatting (name and email) and that should be in the agent deps and tools the agent can call. Enough page context should pass through that if someone is on a product page and asks "do you have this in pink", the agent knows whihch item they mean.Guests can still chat, but history only needs to persist for logged-in users. Docuemtn in output/harness.md how user chat history is stored, what customer fields the agent sees, and how page context is passed.

### What was lacking in my original prompt

_To be filled in once Problem 8 is complete._

---

## Problem 9: Usability improvements

### Prompts

1. okay moving onto problem 9, "Usability improvements". Choose and implement 2 front-end usability improvements and 2 agent/back end usability improvements. Write output/usability.md saying what we added and why it helps a shopper or the business.

### What was lacking in my original prompt

_To be filled in once Problem 9 is complete._

---

## Problem 10: Style the website

### Prompts

1. proble Problem 10, style the website. Add creative design so the site feels like a real storefront. Fonts, color, hierarchy, motion, product presentation, chat feel. Write output/design.md: What you changed and why it should help customers stick around and buy. Keep it concrete.
2. yeah reopn in my browser
3. add an option to clear the chat so that when i reopen it the chat suggestions reappear
4. nice add that to the usability improvements

### What was lacking in my original prompt

_To be filled in once Problem 10 is complete._

---

## Problem 11: Site testing (app check)

### Prompts

1. okay moving onto problem 11 "Site testing (app check)". Test the site and document it in output/app_check.html. Include screenshots and captions for 1. Chat checking the inventory level of an item (honest stock/price from the DB) 2. Dynamic search result cards appearing after a category question 3. One of the usability features we added. The HTML should be easy to grade - a heading for each check, screentshot, and one or two sentences on what hte screenshot proves. Put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths

### What was lacking in my original prompt

The original prompt was detailed and complete (it named the three checks, the output file, the image folder, and the format), so no follow-ups were needed.

---

## Problem 12: Audit trail, safety, finish harness

### Prompts

1. nice bro lets move onto problem 12 "Audit trail, safety, finish harness". Keep an append-only output/audit_trail.json of agent-loop activity. Do not wipe it between runs. Also, think of some safety rules to give the agent and put them in prompts/prompt.md. Finish output/harness.md so it is clear how wthe system works. Modle fields in models.py and why yo chose them, tools and abilities, safety rules, specs

### What was lacking in my original prompt

The prompt bundled three tasks (audit trail, safety rules, finishing the harness) and left the audit entry fields and safety-rule set to my judgment, but it was clear enough that no clarifying follow-ups were needed.

---

## Problem 13: Push to GitHub and submit the URL

### Prompts

1. problem 13 is "Push to Github and submit the URL". Put the code in a folder hw4 and push it to a public github repository (the one you have for me). On canvas, i will submit the repo URL. Do NOT put my real .env, campus_customs.db, or product images in the github repo. Use .gitignore. Include .env.example with placeholders only. See attached for the layout. Readme.md should explain how to run the front end and back end after placing the data pack. [pasted: image of the hw4/ repo folder layout]

### What was lacking in my original prompt

My original prompt did not name the exact repo, so one follow-up was needed to confirm the repository name (chose ai-foundations-hw4) before publishing.
