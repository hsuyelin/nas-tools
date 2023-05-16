---
title: Setup an existing app
order: 7
slug: setup-existing-app
lang: en
layout: tutorial
permalink: /tutorial/setup-existing-app
---

## Setup an existing app <span class="label-beta">BETA</span>

<div class="section-content">
If you would like to setup an existing Slack app written with the beta tools from the <a href="https://api.slack.com/future/intro" target="_blank">next-generation platform</a>, this guide is for you!
</div>

To get started with a new Bolt for Python application take a look at this [Getting Started guide](/bolt-python/tutorial/getting-started-future) instead.

---

### Prerequisites {#prerequisites}

Before we get started, make sure you've followed the [Setting Up step](/bolt-python/tutorial/getting-started-future#setting-up) of the [Getting Started guide](/bolt-python/tutorial/getting-started-future) to install required dependencies.

---

### Set up your app to work with the Slack CLI {#setup-with-cli}

Update your project's version of Bolt (sometimes found in <code><a href="https://pip.pypa.io/en/latest/user_guide/#requirements-files" target="_blank">requirements.txt</a></code>) to the latest `*.dev*` <a href="https://pypi.org/project/slack-bolt/#history" target="_blank">distribution</a> and reinstall your dependencies: `pip install -r requirements.txt`

```text
# with pip
pip install slack-bolt==*.dev*

# in requirements.txt
slack-bolt==*.dev*
```

Then, add a `slack.json` file to your local project root containing the contents of our [template slack.json](https://github.com/slack-samples/bolt-python-starter-template/blob/future/slack.json).

---

### Add your manifest {#manifest-in-code}

Head to [your app's App Config Page](https://api.slack.com/apps) and navigate to Features > App Manifest. Download a copy of your app manifest in the JSON file format.

Add this `manifest.json` to your project root. This represents your project's existing configuration. To get **manifest prediction & validation** in your IDE, include the following line in your `manifest.json` file:

```json
{
  "$schema": "https://raw.githubusercontent.com/slackapi/manifest-schema/main/manifest.schema.json",
  ...
}
```

To learn more about the `manifest.json` take a look at the [Manifest concept](/bolt-python/future/concepts#manifest).

---

Now let's run the Slack CLI command `slack manifest` to generate your manifest. It should contain at least these settings:

```bash
{
  "_metadata": {
    "major_version": 2
  },
  "oauth_config": {
    "token_management_enabled": true  
  },
  "settings": {
    "interactivity": {
      "is_enabled": true
    } 
  },
  "org_deploy_enabled": true       
}
```

You can also run this command to validate your App's configuration with the Slack API:

```bash
slack manifest validate
```

---

### Run your app! {#tada}

Run the Slack CLI command `slack run` to start your app in local development.

The CLI will create and install a new development app for you with its own App ID, allowing you to keep your testing changes separate from your production App).

Now you're ready to start adding [Functions](/bolt-python/future/concepts#functions) and [Workflows](/bolt-python/future/concepts#manifest-workflows) to your app!

---

### Updating your app configuration {#update-app}

You have probably made changes to your app’s manifest (adding a Function or a Workflow, for example). To sync your production app’s configuration with the changes you’ve made locally in your manifest:

1. Authenticate the Slack CLI with your desired production workspace using `slack login`.
2. In your project, head over to `./slack/apps.json` and make sure an entry exists for your workspace with the current `app_id` and `team_id` of the workspace.

    ```bash
    {
      "apps": {
        "<your-workspace-name>": {
          "name": "<your-workspace-name>",
          "app_id": "A041G4M3U00",
          "team_id": "T038J6TH5PF"
        }
      },
      "default": "<your-workspace-name>"
    }
    ```

3. Run `slack install` and select your app. Select your workspace from the list prompt to install.

---

### Conclusion {#conclusion}

Congratulations on migrating your app to the next-generation Slack Platform! 🎉 You can continue your journey by learning about [Manifests](/bolt-python/future/concepts#manifest) or looking into adding [Functions](/bolt-python/future/concepts#functions) and [Workflows](/bolt-python/future/concepts#manifest-workflows) to your app!
