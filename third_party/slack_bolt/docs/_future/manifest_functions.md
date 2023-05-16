---
title: Manifest functions
order: 3
slug: manifest-functions
lang: en
layout: future
---

<div class="section-content">
Your app can [invoke Functions](/bolt-python/future/concepts#functions) defined and created by you (<a href="https://api.slack.com/future/functions/custom" target="_blank">Custom Functions</a>). In order for this to work, Slack must know they exist. Define them in your [App Manifest](/bolt-python/concepts#manifest) also known as `manifest.json` in your project. The next time you `slack run` your app will inform Slack they exist.

<table id="functions_dict">
  <tr>
    <th><h5 id="functions_dict">functions</h5></th>
    <th>dictionary</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>key</code></b></td>
    <td>string</td>
    <td>defines the function's <code>callback_id</code></td>
  </tr>
  <tr>
    <td><b><code>value</code></b></td>
    <td><a href="#function">function</a></td>
    <td>defines the function</td>
  </tr>
</table>

<table id="function">
  <tr>
    <th><h5>function</h5></th>
    <th>object</th>
    <th></th>
  </tr>
  <tr>
    <td><b><code>title</code></b></td>
    <td>string</td>
    <td>defines the title</td>
  </tr>
  <tr>
    <td><b><code>description</code></b></td>
    <td>string</td>
    <td>defines the description</td>
  </tr>
  <tr>
    <td><b><code>input_parameters</code></b></td>
    <td><a href="#parameters">parameters</a></td>
    <td>defines the inputs</td>
  </tr>
  <tr>
    <td><b><code>output_parameters</code></b></td>
    <td><a href="#parameters">parameters</a></td>
    <td>defines the outputs</td>
  </tr>
</table>

</div>

<div>
<span class="annotation">Refer to <a href="https://github.com/slack-samples/bolt-python-starter-template/blob/future/manifest.json" target="_blank">our template project</a> to view a full version of <code>manifest.json</code>.</span>
```json
  "functions": {
    "sample_function": {
      "title": "Sample function",
      "description": "A sample function",
      "input_parameters": {
        "properties": {
          "message": {
            "type": "string",
            "description": "Message to be posted"
          }
        },
        "required": [
          "message"
        ]
      },
      "output_parameters": {
        "properties": {
          "updatedMsg": {
            "type": "string",
            "description": "Updated message to be posted"
          }
        },
        "required": [
          "updatedMsg"
        ]
      }
    }
  }
```
</div>
