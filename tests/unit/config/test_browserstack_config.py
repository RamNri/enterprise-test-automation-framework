from config.browserstack_config import BrowserStackConfig


class TestBrowserStackConfig:

    def test_username_reads_environment_variable(self, monkeypatch):
        monkeypatch.setenv(
            "BROWSERSTACK_USERNAME",
            "test_user"
        )

        assert BrowserStackConfig.username() == "test_user"

    def test_access_key_reads_environment_variable(self, monkeypatch):
        monkeypatch.setenv(
            "BROWSERSTACK_ACCESS_KEY",
            "test_key"
        )

        assert BrowserStackConfig.access_key() == "test_key"

    def test_hub_url(self):
        assert (
            BrowserStackConfig.hub_url() == "https://hub.browserstack.com/wd/hub"
        )

    def test_capabilites(self):
        capabilities = BrowserStackConfig.capabilities()
        assert capabilities["browserName"] == "chrome"
        assert capabilities["browserVersion"] == "latest"
        bstack_options = capabilities["bstack:options"]
        assert bstack_options["os"] == "windows"
        assert bstack_options["osVersion"] == "11"
        assert (  bstack_options["projectName"] == "Enterprise Test Automation Framework")
        assert bstack_options["buildName"] == "Local Build"