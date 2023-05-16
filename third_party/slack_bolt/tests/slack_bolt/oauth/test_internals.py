from slack_bolt.oauth.internals import build_detailed_error, _build_default_install_page_html


class TestOAuthInternals:
    def test_build_detailed_error_invalid_browser(self):
        result = build_detailed_error("invalid_browser")
        assert result.startswith("invalid_browser: This can occur due to page reload, ")

    def test_build_detailed_error_invalid_state(self):
        result = build_detailed_error("invalid_state")
        assert result.startswith("invalid_state: The state parameter is no longer valid.")

    def test_build_detailed_error_missing_code(self):
        result = build_detailed_error("missing_code")
        assert result.startswith("missing_code: The code parameter is missing in this redirection.")

    def test_build_detailed_error_storage_error(self):
        result = build_detailed_error("storage_error")
        assert result.startswith("storage_error: The app's server encountered an issue. Contact the app developer.")

    def test_build_detailed_error_others(self):
        result = build_detailed_error("access_denied")
        assert result.startswith(
            "access_denied: This error code is returned from Slack. Refer to the documents for details."
        )

    def test_build_detailed_error_others_with_tags(self):
        result = build_detailed_error("<b>test</b>")
        assert result.startswith(
            "&lt;b&gt;test&lt;/b&gt;: This error code is returned from Slack. Refer to the documents for details."
        )

    def test_build_default_install_page_html(self):
        test_patterns = [
            {
                "input": "https://slack.com/oauth/v2/authorize?state=random&client_id=111.222&scope=commands",
                "expected": "https://slack.com/oauth/v2/authorize?state=random&amp;client_id=111.222&amp;scope=commands",
            },
            {
                "input": "<b>test</b>",
                "expected": "&lt;b&gt;test&lt;/b&gt;",
            },
        ]
        for pattern in test_patterns:
            url = pattern["input"]
            result = _build_default_install_page_html(url)
            assert url not in result
            assert pattern["expected"] in result
