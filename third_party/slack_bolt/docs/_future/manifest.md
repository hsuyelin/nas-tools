---
title: Manifest
lang: en
slug: manifest
order: 2
layout: future
---


<div class="section-content">

Your project should contain a `manifest.json` file that defines your app's manifest. This is where you'll configure your application name and scopes, declare the functions your app will use, and more.
Refer to the <a href="https://api.slack.com/reference/manifests" target="_blank">App Manifest</a> and <a href="https://api.slack.com/future/manifest#manifest-properties" target="_blank">Manifest Property</a> documentation to learn
about the available manifest configurations.

Notably, the App Manifest informs Slack of the definitions for:

* [Functions](/bolt-python/future/concepts#manifest-functions)
* [Workflows](/bolt-python/future/concepts#manifest-workflows)

`manifest.json` is located at the top level of <a href="https://github.com/slack-samples/bolt-python-starter-template/tree/future" target="_blank">our example projects</a>, along with a `triggers` folder containing
`*_trigger.json` files that define the <a href="https://api.slack.com/future/triggers" target="_blank">triggers</a>
for your app.

<pre class="structure">
.
├── ...
├── manifest.json             # app manifest definition
├── triggers                  # folder with trigger files
│   ├── sample_trigger.json   # trigger definition
│   └── ...
└── ...
</pre>

<br>

#### Linting, prediction & validation

Syntax and formatting checks are required to efficiently edit your `manifest.json`. Multiple IDEs are able to support
this, namely: <a href="https://code.visualstudio.com/docs/languages/json#_mapping-in-the-json" target="_blank">Visual Studio Code</a>, <a href="https://www.jetbrains.com/help/pycharm/json.html#ws_json_schema_add_custom" target="_blank">Pycharm</a>, <a href="https://www.sublimetext.com/" target="_blank">Sublime Text</a> (via <a href="https://packagecontrol.io/packages/LSP-json" target="_blank">LSP-json</a>) and many more.

To get **manifest prediction & validation** in your IDE, include the following line in your `manifest.json` file:

```json
{
  "$schema": "https://raw.githubusercontent.com/slackapi/manifest-schema/main/manifest.schema.json",
  ...
}
```

Using the <a href="https://api.slack.com/future/tools/cli/commands" target="_blank">Slack CLI</a> you can validate your `manifest.json` against the Slack API with:

```bash
slack manifest validate
```

</div>

<div>
<span class="annotation">Refer to <a href="https://github.com/slack-samples/bolt-python-starter-template/blob/future/manifest.json" target="_blank">our template project</a> to view a full version of <code>manifest.json</code>.</span>
```json
{
  "$schema": "https://raw.githubusercontent.com/slackapi/manifest-schema/main/manifest.schema.json",
  "_metadata": {
    "major_version": 2,
  },
  "display_information": {
    "name": "Bolt Template App TEST"
  },
  "features": {
    "app_home": {
      "home_tab_enabled": false,
    },
    "bot_user": {
      "display_name": "Bolt Template App TEST",
      "always_online": false
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "chat:write",
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
  },
  "functions": {},
  "types": {},
  "workflows": {},
  "outgoing_domains": []
}
```
</div>

<details id="common-manifest-types" class="secondary-wrapper">

  <summary class="section-head" markdown="0">
    <h4 class="section-head">Common Manifest Types</h4>
  </summary>

<div>
<div class="secondary-content">

<table id="parameters">
  <tr>
    <th><h5>parameters</h5></th>
    <th>object</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>properties</code></b></td>
    <td><a href="#properties">properties</a></td>
    <td>defines the properties</td>
  </tr>
  <tr>
    <td><b><code>required</code></b></td>
    <td>list[string]</td>
    <td>defines the properties required by the function</td>
  </tr>
</table>

<table id="properties">
  <tr>
    <th><h5>properties</h5></th>
    <th>dictionary</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>key</code></b></td>
    <td>string</td>
    <td>defines the property name</td>
  </tr>
  <tr>
    <td><b><code>value</code></b></td>
    <td><a href="#property">property</a></td>
    <td>defines the property</td>
  </tr>
</table>

<table id="property">
  <tr>
    <th><h5>property</h5></th>
    <th>object</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>type</code></b></td>
    <td>string</td>
    <td>defines the property type</td>
  </tr>
  <tr>
    <td><b><code>description</code></b></td>
    <td>string</td>
    <td>defines the property description</td>
  </tr>
</table>
</div>

```json
"$comment": "sample parameters object"
"*_parameters":{
  "properties": {
    "property_0_name": {
      "type": "string",
      "description": "this is my first property"
    },
    "property_1_name": {
      "type": "integer",
      "description": "this is my second property"
    }
  },
  "required": [
    "property_0_name"
  ]
}
```

</div>
</details>
