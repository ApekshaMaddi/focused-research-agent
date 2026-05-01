# Focused Research Agent — Simplified Streamlit UI Guide

This guide gives you two things:

1. a **much simpler Streamlit first slice**
2. a **line-by-line explanation** so you can understand it and explain it in an interview

The code follows your requested rules:

- `streamlit_app.py` is inside the `ui` package
- no `lambda`
- no list comprehensions
- no UI-side question validation logic beyond sending the question to the backend
- no hardcoded API base URL or research path inside code logic
- Sonar-friendly refactor for `extract_error_message()`
- module-level and method-level docstrings are included

---

## 1. Final file placement inside your project

Put these files inside your existing project here:

```text
src/
  focused_research_agent/
    ui/
      __init__.py
      ui_config.py
      api_client.py
      session_state.py
      renderers.py
      streamlit_app.py
```

This keeps the UI package structure consistent with your API package approach from the handoff. The handoff also says the next phase should keep Streamlit thin and use the existing FastAPI backend rather than duplicating the core engine. fileciteturn0file0

---

## 2. Environment variables to add

Add these to your `.env` file:

```env
FOCUSED_RESEARCH_AGENT_API_BASE_URL=http://localhost:8000
FOCUSED_RESEARCH_AGENT_API_RESEARCH_PATH=/api/v1/research
FOCUSED_RESEARCH_AGENT_API_TIMEOUT_SECONDS=60
```

Why this is better:

- the API base URL is not hardcoded inside Python code
- the research endpoint path is not hardcoded inside Python code
- timeout is configurable without changing code

---

## 3. How to run the backend and Streamlit app

From the project root:

### Run FastAPI backend

```bash
uv run uvicorn --factory focused_research_agent.api.app:create_app --reload
```

That matches the handoff's intended API startup command. fileciteturn0file0

### Run Streamlit

```bash
uv run streamlit run src/focused_research_agent/ui/streamlit_app.py
```

Why this works:

- the file lives inside the `ui` package, as you wanted
- you still run it by file path from the project root
- the code uses package imports like `focused_research_agent.ui...`, which fits your existing project layout

If imports ever fail on a fresh environment, run:

```bash
uv sync
```

and then retry.

---

## 4. Very simple architecture of this UI slice

Keep this mental model:

```text
Streamlit page
   -> API client
      -> FastAPI /api/v1/research
         -> application layer
            -> graph
               -> providers
```

The Streamlit UI is only a thin presentation layer. That matches the handoff and preserves your current architecture. fileciteturn0file0

---

## 5. What each file does in one sentence

### `ui_config.py`
Loads UI settings from environment variables.

### `api_client.py`
Sends the question to the backend and converts HTTP/network problems into simple custom exceptions.

### `session_state.py`
Stores the last question, the last result, and the last error in Streamlit session state.

### `renderers.py`
Contains only UI display code.

### `streamlit_app.py`
Acts as the thin page entry point and wires everything together.

---

## 6. Why this version is simpler than the previous one

### Before
The earlier version had more generic utility behavior and more mixed concerns.

### Now
This version is simpler because:

- config is separated into one tiny file
- the page file is short and only coordinates flow
- API errors are mapped into very obvious exception names
- rendering is split into small display-only functions
- question validation is left to the backend, exactly as you requested
- `extract_error_message()` was broken into smaller helpers to reduce Sonar cognitive complexity

---

# 7. Line-by-line explanation

Below, I explain each file with line numbers so you can open the real file and follow along without scrolling through chat.

---

## A. `src/focused_research_agent/ui/__init__.py`

### Code
This file has only one line.

### Line-by-line explanation

- **Line 1**: Adds a module docstring so the package is documented and easy to understand.

Why this file exists:

- it tells Python this folder is a package
- it keeps the package consistent with your project structure

---

## B. `src/focused_research_agent/ui/ui_config.py`

### Purpose
This file reads configuration from `.env` and returns one small settings object.

### Line-by-line explanation

- **Lines 1 to 7**: Module docstring. It explains that this file keeps configuration in one place and avoids hardcoding the API base URL, path, and timeout.
- **Line 9**: Imports `os` so we can read environment variables.
- **Line 10**: Imports `dataclass` so we can group related UI config values in one small class.
- **Line 12**: Imports `load_dotenv` so the `.env` file is loaded automatically.
- **Lines 15 to 16**: Defines `UIConfigError`. This custom exception is used when a required config value is missing or invalid.
- **Line 19**: `@dataclass(frozen=True)` means `UISettings` is a simple data container and should not be changed after creation.
- **Lines 20 to 27**: Docstring for `UISettings`. It explains what each config field means.
- **Lines 29 to 31**: The three config fields are declared: `api_base_url`, `research_path`, and `timeout_seconds`.
- **Line 34**: Starts `load_ui_settings()`.
- **Lines 35 to 43**: Function docstring explaining what it returns and when it raises an error.
- **Line 44**: Calls `load_dotenv()` so values from `.env` become available in `os.getenv()`.
- **Line 46**: Reads `FOCUSED_RESEARCH_AGENT_API_BASE_URL` using a helper that forces the value to exist.
- **Line 47**: Reads `FOCUSED_RESEARCH_AGENT_API_RESEARCH_PATH` the same way.
- **Line 48**: Reads timeout as text first.
- **Line 49**: Converts the timeout text into a float using a helper.
- **Lines 51 to 55**: Creates one `UISettings` object that groups all three values together.
- **Line 56**: Returns that settings object.
- **Line 59**: Starts `get_required_env()`.
- **Lines 60 to 70**: Function docstring.
- **Line 71**: Reads one environment variable.
- **Lines 73 to 74**: If the variable does not exist, raise `UIConfigError`.
- **Lines 76 to 77**: If the variable exists but is blank, also raise `UIConfigError`.
- **Line 79**: Returns the non-empty value.
- **Line 82**: Starts `parse_timeout_seconds()`.
- **Lines 83 to 93**: Function docstring.
- **Lines 94 to 95**: Tries to convert timeout text into a float.
- **Lines 96 to 99**: If conversion fails, raises `UIConfigError` with a clear message.
- **Line 101**: Returns the numeric timeout.

### Why this file is good for interviews

You can explain it like this:

> `ui_config.py` keeps configuration out of the page and out of the API client. It reads required values from the environment, validates them once, and returns a small immutable settings object.

---

## C. `src/focused_research_agent/ui/api_client.py`

### Purpose
This file is the only place that knows about `requests`, URLs, status codes, JSON parsing, timeout errors, and connection errors.

### Part 1 — imports and exception classes

- **Lines 1 to 5**: Module docstring. It says the Streamlit page should not need to deal with raw HTTP details.
- **Line 8**: Imports `Any` for type hints.
- **Line 10**: Imports `requests` for HTTP calls.
- **Line 12**: Imports `UISettings` so the client can use the config values.
- **Lines 15 to 16**: Defines base exception `ApiClientError`.
- **Lines 19 to 20**: Defines `ApiBadRequestError` for HTTP 400.
- **Lines 23 to 24**: Defines `ApiValidationError` for HTTP 422.
- **Lines 27 to 28**: Defines `ApiServerError` for HTTP 500 and other 5xx responses.
- **Lines 31 to 32**: Defines `ApiTimeoutError`.
- **Lines 35 to 36**: Defines `ApiConnectionError`.
- **Lines 39 to 40**: Defines `ApiResponseFormatError`.

Why these custom exceptions help:

- the page can show different user-friendly messages
- the page does not need to inspect HTTP status codes directly

### Part 2 — `ResearchApiClient` class

- **Line 43**: Starts `ResearchApiClient`.
- **Lines 44 to 49**: Class docstring explaining that it is a very small client and that it receives settings.
- **Line 51**: Starts `__init__()`.
- **Lines 52 to 56**: Constructor docstring.
- **Line 57**: Saves the settings on `self` so all methods can use them.
- **Line 59**: Starts `submit_question()`.
- **Lines 60 to 76**: Method docstring describing inputs, outputs, and possible errors.
- **Lines 77 to 80**: Builds the full endpoint URL by calling `build_url()` with the base URL and path from config.
- **Line 81**: Builds the request payload as `{"question": question}`.
- **Line 83**: Starts a `try` block around the HTTP request.
- **Lines 84 to 88**: Sends a POST request to the backend using `requests.post()`.
- **Lines 89 to 90**: If the request times out, convert that into `ApiTimeoutError`.
- **Lines 91 to 92**: If the backend cannot be reached, convert that into `ApiConnectionError`.
- **Lines 93 to 94**: Any other `requests` problem becomes `ApiClientError`.
- **Line 96**: Checks the HTTP status code and raises a custom exception when needed.
- **Line 98**: Parses the response JSON.
- **Lines 99 to 100**: Makes sure the JSON is a dictionary, because the UI expects a JSON object.
- **Lines 102 to 103**: Normalizes the backend result and returns it.

### Part 3 — URL builder

- **Line 106**: Starts `build_url()`.
- **Lines 107 to 115**: Function docstring.
- **Lines 116 to 117**: Copies the input values into local variables.
- **Lines 119 to 120**: If the base URL ends with `/`, remove it.
- **Lines 122 to 123**: If the path does not start with `/`, add it.
- **Lines 125 to 126**: Join the cleaned base URL and cleaned path and return the full URL.

Why this is better than hardcoding:

- the base URL comes from config
- the path comes from config
- this helper joins them safely in one place

### Part 4 — status-code handling

- **Line 129**: Starts `raise_for_error_status()`.
- **Lines 130 to 140**: Function docstring.
- **Line 141**: Reads the status code into a local variable.
- **Lines 143 to 144**: If the status code is below 400, there is no error, so return.
- **Line 146**: Extracts a readable error message from the response.
- **Lines 148 to 149**: HTTP 400 becomes `ApiBadRequestError`.
- **Lines 151 to 152**: HTTP 422 becomes `ApiValidationError`.
- **Lines 154 to 155**: Any 5xx becomes `ApiServerError`.
- **Line 157**: Any other 4xx/5xx becomes generic `ApiClientError`.

### Part 5 — JSON parsing

- **Line 160**: Starts `parse_json_body()`.
- **Lines 161 to 171**: Function docstring.
- **Lines 172 to 173**: Tries to parse JSON from the response.
- **Lines 174 to 175**: If parsing fails, raises `ApiResponseFormatError`.
- **Line 177**: Returns parsed JSON.

### Part 6 — result normalization

- **Line 180**: Starts `normalize_result_payload()`.
- **Lines 181 to 188**: Function docstring.
- **Line 189**: Creates an empty result dictionary.
- **Lines 191 to 195**: Copies simple top-level fields with safe defaults.
- **Lines 197 to 200**: Reads `queries`; if missing, uses an empty list.
- **Lines 202 to 205**: Reads `sources`; if missing, uses an empty list.
- **Lines 207 to 210**: Reads `citations`; if missing, uses an empty list.
- **Lines 212 to 215**: Reads `errors`; if missing, uses an empty list.
- **Line 217**: Returns the normalized dictionary.

Why normalization is useful:

- the renderer can safely do `result.get("sources")`
- missing optional fields do not crash the page

### Part 7 — Sonar-friendly `extract_error_message()`

This is the part you specifically asked about.

#### Why Sonar complained before
A function like `extract_error_message()` often becomes messy because it tries to handle many cases in one place:

- no JSON
- JSON but not a dict
- `detail` is a string
- `detail` is a list
- `detail` is a dict
- top-level `message`
- top-level `error`
- top-level `errors`

If all of that stays inside one function, cognitive complexity increases.

#### What we changed
We kept `extract_error_message()` very small and moved the detailed branches into helpers.

### `extract_error_message()` explanation

- **Line 220**: Starts `extract_error_message()`.
- **Lines 221 to 232**: Function docstring.
- **Line 233**: Reads JSON payload using a helper.
- **Lines 235 to 236**: If there is no usable JSON, fall back to raw text.
- **Lines 238 to 239**: If the payload is not a dictionary, return a default message like `HTTP 500`.
- **Lines 241 to 243**: Try reading a message from `detail` first.
- **Lines 245 to 247**: If that failed, try top-level `message` or `error`.
- **Lines 249 to 251**: If that failed, try the top-level `errors` list.
- **Line 253**: If nothing worked, return a default HTTP message.

This function is now easy to read because it says:

1. get payload
2. try detail
3. try top-level fields
4. try errors list
5. fallback

### Helper explanations for the error-message flow

#### `read_json_payload()`
- **Lines 256 to 270**: Tries to parse JSON from the response and returns `None` if parsing fails.

#### `read_text_message()`
- **Lines 273 to 287**: Reads raw response text and falls back to a default message if the text is empty.

#### `read_message_from_detail()`
- **Lines 290 to 312**: Reads the `detail` field and handles three cases:
  - string
  - list
  - dictionary

#### `join_validation_details()`
- **Lines 315 to 334**: Turns a list of validation detail items into one readable string separated by `; `.
- Important: this uses a regular `for` loop, not a list comprehension.

#### `read_message_from_detail_dict()`
- **Lines 337 to 356**: Reads either `message` or `error` from a detail dictionary.

#### `read_top_level_message()`
- **Lines 359 to 378**: Reads either `message` or `error` from the top level of the payload.

#### `read_errors_list_message()`
- **Lines 381 to 404**: Reads the top-level `errors` list and joins it into one string.
- Important: this also uses a regular loop, not a list comprehension.

#### `format_validation_detail()`
- **Lines 407 to 433**: Converts one FastAPI/Pydantic validation detail item into readable text.
- **Lines 416 to 417**: If the item is not a dictionary, just convert it to text.
- **Lines 419 to 420**: Read the validation message.
- **Lines 422 to 431**: If there is a location like `("body", "question")`, convert it into readable text like `body -> question: ...`.
- Important: the location parts are built using a normal `for` loop, not a list comprehension.

#### `default_http_message()`
- **Lines 436 to 445**: Returns a simple fallback like `HTTP 500`.

### Interview-friendly explanation for `api_client.py`

> `api_client.py` keeps the Streamlit page clean by owning all HTTP concerns: URL building, POST requests, status-code mapping, JSON parsing, and readable error extraction. I also refactored the error-extraction logic into small helper functions so it stays easy to understand and satisfies Sonar's cognitive complexity rule.

---

## D. `src/focused_research_agent/ui/session_state.py`

### Purpose
This file stores the current UI state between Streamlit reruns.

### Line-by-line explanation

- **Lines 1 to 5**: Module docstring. It says this module keeps UI-only state in one place.
- **Line 7**: Imports `Any` for type hints.
- **Line 9**: Imports Streamlit.
- **Lines 12 to 14**: Defines the three session-state keys as constants.
- **Line 17**: Starts `initialize_session_state()`.
- **Lines 18 to 22**: Function docstring.
- **Lines 23 to 24**: If `last_question` does not exist yet, create it with an empty string.
- **Lines 26 to 27**: If `latest_result` does not exist yet, create it with `None`.
- **Lines 29 to 30**: If `latest_error` does not exist yet, create it with `None`.
- **Line 33**: Starts `save_result()`.
- **Lines 34 to 39**: Function docstring.
- **Line 40**: Save the submitted question.
- **Line 41**: Save the successful result.
- **Line 42**: Clear any previous error.
- **Line 45**: Starts `save_error()`.
- **Lines 46 to 51**: Function docstring.
- **Line 52**: Save the submitted question.
- **Line 53**: Clear any previous result.
- **Line 54**: Save the new error message.
- **Line 57**: Starts `get_last_question()`.
- **Lines 58 to 62**: Function docstring.
- **Line 63**: Reads the last question from session state and uses an empty string if it is missing.
- **Lines 65 to 66**: If the value is a string, return it.
- **Line 68**: Otherwise return an empty string.
- **Line 71**: Starts `get_latest_result()`.
- **Lines 72 to 76**: Function docstring.
- **Line 77**: Reads the saved result.
- **Lines 79 to 80**: If the value is a dictionary, return it.
- **Line 82**: Otherwise return `None`.
- **Line 85**: Starts `get_latest_error()`.
- **Lines 86 to 90**: Function docstring.
- **Line 91**: Reads the saved error.
- **Lines 93 to 95**: If the value is a non-empty string, return it.
- **Line 97**: Otherwise return `None`.

### Interview-friendly explanation

> `session_state.py` keeps the page simple by centralizing Streamlit session-state reads and writes. It stores only UI state: the last question, the latest result, and the latest error.

---

## E. `src/focused_research_agent/ui/renderers.py`

### Purpose
This file contains only display code.

### Part 1 — page header and form

- **Lines 1 to 5**: Module docstring explaining that this file is presentation-only.
- **Line 7**: Imports `Any` for type hints.
- **Line 9**: Imports Streamlit.
- **Line 12**: Starts `render_page_header()`.
- **Lines 13 to 17**: Function docstring.
- **Line 18**: Shows the page title.
- **Line 19**: Shows a short caption that explains the UI is thin.
- **Line 20**: Shows the backend base URL so local debugging is easier.
- **Line 23**: Starts `render_question_form()`.
- **Lines 24 to 31**: Function docstring.
- **Line 32**: Starts a Streamlit form. The form groups input and submit action together.
- **Lines 33 to 37**: Creates a text area for the question.
- **Line 38**: Creates the submit button.
- **Line 40**: Returns both values: whether the form was submitted and the question text.

### Part 2 — top-level error and result rendering

- **Line 43**: Starts `render_error_message()`.
- **Lines 44 to 48**: Function docstring.
- **Line 49**: Shows a red Streamlit error box.
- **Line 52**: Starts `render_result()`.
- **Lines 53 to 57**: Function docstring.
- **Line 58**: Adds a divider.
- **Line 59**: Shows the `Result` section heading.
- **Lines 61 to 66**: Calls small helper render functions in order.

This is important because it keeps `render_result()` easy to read.

### Part 3 — basic fields and answer

- **Line 69**: Starts `render_basic_fields()`.
- **Lines 70 to 74**: Function docstring.
- **Lines 75 to 77**: Reads `question`, `status`, and `run_id` from the result.
- **Lines 79 to 80**: If a question exists, display it.
- **Lines 82 to 83**: If a status exists, display it.
- **Lines 85 to 86**: If a run ID exists, display it.
- **Line 89**: Starts `render_answer_section()`.
- **Lines 90 to 94**: Function docstring.
- **Line 95**: Shows the `Answer` section heading.
- **Line 97**: Reads the answer field.
- **Lines 98 to 101**: If the answer is a non-empty string, display it and return.
- **Line 103**: Otherwise show an info message saying no answer was returned.

### Part 4 — source rendering

- **Line 106**: Starts `render_sources_section()`.
- **Lines 107 to 111**: Function docstring.
- **Line 112**: Shows the `Sources` heading.
- **Line 114**: Reads the `sources` field.
- **Lines 115 to 117**: If `sources` is not a list, show a fallback message and return.
- **Lines 119 to 121**: If the list is empty, show a fallback message and return.
- **Line 123**: Starts source numbering at 1.
- **Lines 124 to 126**: Loops through sources and renders each one.
- **Line 129**: Starts `render_single_source()`.
- **Lines 130 to 135**: Function docstring.
- **Lines 136 to 138**: If the source is not a dictionary, just display it directly.
- **Lines 140 to 142**: Reads title, URL, and snippet.
- **Lines 144 to 145**: If the title is blank, create a fallback title.
- **Lines 147 to 153**: If a real URL exists, show the source title as a clickable link. Otherwise just show the title.
- **Lines 155 to 157**: If a snippet exists, display it.
- **Line 160**: Starts `read_source_snippet()`.
- **Lines 161 to 168**: Function docstring.
- **Lines 169 to 171**: Use `snippet` if present.
- **Lines 173 to 175**: Otherwise use `content` if present.
- **Lines 177 to 178**: Otherwise return `summary`.

### Part 5 — citations and workflow errors

- **Line 181**: Starts `render_citations_section()`.
- **Lines 182 to 186**: Function docstring.
- **Line 187**: Shows the `Citations` heading.
- **Line 189**: Reads the `citations` field.
- **Lines 190 to 192**: If `citations` is not a list, show a fallback message and return.
- **Lines 194 to 196**: If the list is empty, show a fallback message and return.
- **Line 198**: Starts numbering at 1.
- **Lines 199 to 205**: Loops through citations. If one citation is a dictionary, show it as JSON. Otherwise show plain text.
- **Line 208**: Starts `render_workflow_errors_section()`.
- **Lines 209 to 213**: Function docstring.
- **Line 214**: Reads the `errors` field.
- **Lines 215 to 216**: If it is not a list, return.
- **Lines 218 to 219**: If the list is empty, return.
- **Line 221**: Shows the `Workflow errors` heading.
- **Lines 223 to 224**: Displays each workflow error as a warning.

This is important because backend workflow errors are different from top-level transport failures. That distinction already exists in your backend handoff. fileciteturn0file0

### Part 6 — trace, scope, and queries

- **Line 227**: Starts `render_trace_section()`.
- **Lines 228 to 232**: Function docstring.
- **Line 233**: Creates an expander called `Research trace`.
- **Lines 234 to 235**: Renders scope and queries inside that expander.
- **Line 238**: Starts `render_scope_section()`.
- **Lines 239 to 243**: Function docstring.
- **Line 244**: Shows the `Scope` heading.
- **Line 246**: Reads the `scope` field.
- **Lines 247 to 249**: If `scope` is missing, show a fallback message and return.
- **Lines 251 to 253**: If `scope` is a dictionary, show it as JSON.
- **Lines 255 to 257**: If `scope` is a list, show it as JSON.
- **Lines 259 to 262**: If `scope` is a blank string, show a fallback message and return.
- **Line 264**: Otherwise show the scope normally.
- **Line 267**: Starts `render_queries_section()`.
- **Lines 268 to 272**: Function docstring.
- **Line 273**: Shows the `Generated queries` heading.
- **Line 275**: Reads the `queries` field.
- **Lines 276 to 278**: If `queries` is not a list, show a fallback message and return.
- **Lines 280 to 282**: If the list is empty, show a fallback message and return.
- **Line 284**: Starts numbering at 1.
- **Lines 285 to 287**: Loops through queries and displays them.

### Interview-friendly explanation

> `renderers.py` is presentation-only. It takes already-prepared data and displays it. It never calls the backend and never owns business logic. That keeps the page entry small and respects separation of responsibilities.

---

## F. `src/focused_research_agent/ui/streamlit_app.py`

### Purpose
This is the entry page that wires together config, API client, session state, and renderers.

### Line-by-line explanation

- **Lines 1 to 13**: Module docstring explaining the role of the page file.
- **Line 15**: Imports Streamlit.
- **Lines 17 to 25**: Imports the API client and the custom API error classes.
- **Lines 26 to 31**: Imports renderer functions.
- **Lines 32 to 39**: Imports session-state helpers.
- **Line 40**: Imports UI config loading and config error class.
- **Line 43**: Starts `main()`.
- **Line 44**: Function docstring.
- **Lines 45 to 49**: Sets Streamlit page configuration.
- **Line 51**: Initializes session-state keys.
- **Lines 53 to 57**: Loads settings from `.env`. If settings are missing or invalid, show the error and stop the page.
- **Line 59**: Creates the API client using the settings.
- **Line 61**: Renders the page header.
- **Line 63**: Reads the last submitted question from session state.
- **Line 64**: Renders the form and receives two values: `submitted` and `question`.
- **Lines 66 to 67**: If the user clicked submit, call `handle_submission()`.
- **Line 69**: Render the latest saved output.
- **Line 72**: Starts `handle_submission()`.
- **Lines 73 to 78**: Function docstring.
- **Lines 79 to 81**: Shows a spinner while calling the backend.
- **Lines 82 to 83**: If backend validation fails, save a validation error.
- **Lines 84 to 85**: If backend returns HTTP 400, save a bad-request error.
- **Lines 86 to 87**: If backend returns HTTP 5xx, save a server error.
- **Lines 88 to 89**: If the request times out, save a timeout error.
- **Lines 90 to 91**: If connection fails, save a connection error.
- **Lines 92 to 93**: Any other client-side HTTP problem becomes a generic API error.
- **Lines 94 to 95**: If no exception happened, save the successful result.
- **Line 98**: Starts `render_saved_output()`.
- **Line 99**: Function docstring.
- **Line 100**: Read the latest saved error.
- **Lines 101 to 102**: If an error exists, render it.
- **Line 104**: Read the latest saved result.
- **Lines 105 to 106**: If a result exists, render it.
- **Lines 109 to 110**: Standard Python entry point. If the file is run directly, call `main()`.

### Why there is no UI question validation here

Because you explicitly asked for that.

This page does **not** reject blank or short questions locally.
It sends the question to the backend and shows the backend's error message.
That keeps validation ownership on the backend.

### Interview-friendly explanation

> `streamlit_app.py` is intentionally thin. It loads config, creates the API client, renders the form, calls the backend, and displays either the latest error or the latest result. It does not duplicate research logic and it does not own validation rules.

---

# 8. Manual smoke test checklist

Run these tests after starting both FastAPI and Streamlit.

### Test 1 — success case
Submit a normal question.

Expected:
- answer shows
- sources show
- citations show
- research trace shows

### Test 2 — blank question
Submit an empty question.

Expected:
- the backend rejects it
- the UI shows the backend validation error

### Test 3 — punctuation-only question
Submit `.`

Expected:
- the backend rejects it
- the UI shows the backend validation error

### Test 4 — short meaningless question
Submit `a`

Expected:
- the backend rejects it
- the UI shows the backend validation error

### Test 5 — connection failure
Stop FastAPI and submit any question.

Expected:
- the UI shows a connection error

### Test 6 — timeout failure
Temporarily set this in `.env`:

```env
FOCUSED_RESEARCH_AGENT_API_TIMEOUT_SECONDS=0.001
```

Expected:
- the UI shows a timeout error

### Test 7 — server error
Temporarily force a backend `RuntimeError` in a safe local test path.

Expected:
- the UI shows a server error

Your handoff already says API-side tests cover the centralized 400 and 500 behavior, so manual smoke testing here is mainly about confirming the Streamlit integration and user experience. fileciteturn0file0

---

# 9. Best short interview answer for this Streamlit phase

You can say:

> In Phase 2, I added a thin Streamlit UI on top of the existing FastAPI backend. I kept the architecture consistent with the rest of the project: the page layer is thin, the API client owns HTTP concerns, the renderer module owns presentation, and the backend still owns validation and research execution. I also kept configuration outside the code by reading the API base URL, endpoint path, and timeout from environment variables. For maintainability, I refactored response error extraction into smaller helper functions so the code stayed simple and Sonar-friendly.

---

# 10. What to open first

Open the files in this order:

1. `streamlit_app.py`
2. `ui_config.py`
3. `api_client.py`
4. `session_state.py`
5. `renderers.py`

That order makes the learning curve easier.

---

# 11. Files prepared for you

I also prepared a ready-to-copy folder/zip with the actual Python files.

Use that together with this guide.
