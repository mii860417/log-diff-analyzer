import streamlit as st


st.set_page_config(
    page_title="Log Diff Analyzer",
    page_icon="📊",
    layout="wide",
)


def load_example(example_name: str):
    examples = {
        "Deployment introduced new error": (
            """INFO App started
INFO Connecting to database
INFO Fetching user profile
WARN Slow response detected
INFO Request finished""",
            """INFO App started
INFO Connecting to database
INFO Fetching user profile
WARN Slow response detected
ERROR Database connection timeout
INFO Request finished""",
        ),
        "Regression added API failure": (
            """INFO Login request sent
INFO Token received
INFO Fetching dashboard data
INFO Dashboard loaded successfully""",
            """INFO Login request sent
INFO Token received
INFO Fetching dashboard data
ERROR API 500 Internal Server Error
ERROR Failed to load dashboard""",
        ),
        "Log cleanup removed warning": (
            """INFO App booting
WARN Deprecated config detected
INFO Service initialized
INFO Listening on port 8080""",
            """INFO App booting
INFO Service initialized
INFO Listening on port 8080""",
        ),
        "Android crash symptom appeared": (
            """01-10 10:00:00.000 I/MainActivity: App launched
01-10 10:00:01.100 I/AuthManager: Token valid
01-10 10:00:02.200 I/HomePage: Render success""",
            """01-10 10:00:00.000 I/MainActivity: App launched
01-10 10:00:01.100 I/AuthManager: Token valid
01-10 10:00:02.200 I/HomePage: Render success
01-10 10:00:03.300 E/AndroidRuntime: FATAL EXCEPTION: main
01-10 10:00:03.301 E/AndroidRuntime: java.lang.NullPointerException""",
        ),
    }
    return examples[example_name]


def normalize_lines(text: str):
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def is_error_line(line: str) -> bool:
    keywords = ["error", "exception", "fatal", "fail", "failed", "crash", "timeout"]
    lowered = line.lower()
    return any(keyword in lowered for keyword in keywords)


def is_warning_line(line: str) -> bool:
    keywords = ["warn", "warning", "deprecated"]
    lowered = line.lower()
    return any(keyword in lowered for keyword in keywords)


def analyze_logs(log_a: str, log_b: str):
    lines_a = normalize_lines(log_a)
    lines_b = normalize_lines(log_b)

    set_a = set(lines_a)
    set_b = set(lines_b)

    added = [line for line in lines_b if line not in set_a]
    removed = [line for line in lines_a if line not in set_b]

    added_errors = [line for line in added if is_error_line(line)]
    added_warnings = [line for line in added if is_warning_line(line)]

    return {
        "added": added,
        "removed": removed,
        "added_errors": added_errors,
        "added_warnings": added_warnings,
        "count_a": len(lines_a),
        "count_b": len(lines_b),
    }


st.title("📊 Log Diff Analyzer")
st.caption(
    "Compare two logs and quickly detect added lines, removed lines, and newly introduced errors."
)

with st.sidebar:
    st.header("Examples")
    example_choice = st.selectbox(
        "Load a sample",
        [
            "None",
            "Deployment introduced new error",
            "Regression added API failure",
            "Log cleanup removed warning",
            "Android crash symptom appeared",
        ],
    )

    st.markdown("---")
    st.markdown("### What this tool does")
    st.markdown(
        """
- Compare two logs
- Detect added lines
- Detect removed lines
- Highlight new error and warning lines
"""
    )

if example_choice != "None":
    default_log_a, default_log_b = load_example(example_choice)
else:
    default_log_a, default_log_b = "", ""

col1, col2 = st.columns(2)

with col1:
    log_a = st.text_area(
        "Log A (Before)",
        value=default_log_a,
        height=320,
        placeholder="Paste the original log here...",
    )

with col2:
    log_b = st.text_area(
        "Log B (After)",
        value=default_log_b,
        height=320,
        placeholder="Paste the updated log here...",
    )

analyze_clicked = st.button("Analyze Differences", type="primary")

if analyze_clicked:
    result = analyze_logs(log_a, log_b)

    st.success("Analysis complete")

    st.markdown("## Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    summary_col1.metric("Log A Lines", result["count_a"])
    summary_col2.metric("Log B Lines", result["count_b"])
    summary_col3.metric("Added Lines", len(result["added"]))
    summary_col4.metric("Removed Lines", len(result["removed"]))

    if result["added_errors"]:
        st.markdown("### Newly Added Error Lines")
        for line in result["added_errors"]:
            st.error(line)

    if result["added_warnings"]:
        st.markdown("### Newly Added Warning Lines")
        for line in result["added_warnings"]:
            st.warning(line)

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.markdown("### Added Lines")
        if result["added"]:
            for line in result["added"]:
                if is_error_line(line):
                    st.error(line)
                elif is_warning_line(line):
                    st.warning(line)
                else:
                    st.write(line)
        else:
            st.success("No added lines detected.")

    with result_col2:
        st.markdown("### Removed Lines")
        if result["removed"]:
            for line in result["removed"]:
                st.write(line)
        else:
            st.success("No removed lines detected.")

st.markdown("---")
st.markdown("### Good use cases")
st.markdown(
    """
- Compare logs before and after deployment  
- Detect regression-related log changes  
- Find newly introduced errors in CI or app logs  
- Compare Android logs across two test runs  
"""
)
st.caption("If this tool helped you, please ⭐ the GitHub repo.")